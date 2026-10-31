"""Measurement integrity tests; never assert host-dependent speed or model accuracy."""

import contextlib
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from ml import benchmark
from ml.audit import AuditError, digest, encoded


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            (benchmark.ROOT / "docs/benchmarks/20261031-e07-fixture-analysis.json").read_bytes()
        )

    def test_frozen_record_binds_inputs_code_and_no_train_outcomes(self):
        benchmark.verify_report(self.report)
        self.assertEqual(len(self.report["resources"]), 9)
        self.assertEqual(self.report["mechanics_cases_passed"], 17)
        serialized = encoded(self.report)
        self.assertNotIn(b'"reviews":', serialized)
        self.assertNotIn(b'"text":', serialized)
        self.assertNotIn(str(benchmark.ROOT).encode(), serialized)
        self.assertIsNone(self.report["baseline_comparison"])

    def test_checksum_input_measurement_and_implementation_tampering_fail(self):
        mutations = (
            lambda r: r.update(passed=False),
            lambda r: r["implementation_sha256"].pop("ml/benchmark.py"),
            lambda r: r["resources"][0]["samples"][0].update(input_sha256="0" * 64),
            lambda r: r["resources"][0]["samples"][0].update(wall_seconds=float("nan")),
            lambda r: r["resources"][0]["samples"][0].update(peak_rss_bytes=0),
            lambda r: r["resources"][0]["summary"].update(wall_median_seconds=999),
            lambda r: r["resources"][0]["samples"][0].update(score=100),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.report)
                mutation(changed)
                changed.pop("report_sha256")
                changed["report_sha256"] = digest(encoded(changed))
                with self.assertRaises(AuditError):
                    benchmark.verify_report(changed)
        changed = copy.deepcopy(self.report)
        changed["report_sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "checksum"):
            benchmark.verify_report(changed)

    def test_summary_preserves_missing_memory_and_uses_median_and_max(self):
        samples = [
            {"wall_seconds": v, "cpu_seconds": v / 2, "peak_rss_bytes": None, "passed": True}
            for v in (1, 9, 2)
        ]
        result = benchmark.summarize(samples)
        self.assertEqual(result["wall_median_seconds"], 2)
        self.assertEqual(result["wall_max_seconds"], 9)
        self.assertIsNone(result["peak_rss_max_bytes"])
        with self.assertRaises(AuditError):
            benchmark.summarize([])

    def test_workload_ceilings_are_exact_and_unknown_cases_reject(self):
        self.assertEqual(len(benchmark.request_case("json_exact_1mib")[0]), benchmark.LIMIT)
        self.assertEqual(len(benchmark.request_case("over_1mib")[0]), benchmark.LIMIT + 1)
        payload = json.loads(benchmark.request_case("aggregate_250000")[0])
        self.assertEqual(len(payload["reviews"]), 500)
        self.assertEqual(sum(len(r["text"]) for r in payload["reviews"]), 250000)
        payload = json.loads(benchmark.request_case("single_5000")[0])
        self.assertEqual(len(payload["reviews"][0]["text"]), 5000)
        with self.assertRaises(AuditError):
            benchmark.request_case("arbitrary_command")

    def test_output_is_create_only_and_confined_to_ignored_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(benchmark, "ROOT", root):
                with self.assertRaises(AuditError):
                    benchmark.write_report(root / "outside.json", {})
                target = root / "ml/artifacts/record.json"
                benchmark.write_report(target, {"passed": True})
                with self.assertRaises(FileExistsError):
                    benchmark.write_report(target, {})
                self.assertEqual(json.loads(target.read_bytes()), {"passed": True})

    def test_each_case_uses_three_bounded_fresh_processes(self):
        by_id = {c["case_id"]: c["samples"][0] for c in self.report["resources"]}

        def child(command, **kwargs):
            self.assertEqual(
                command[:4], [benchmark.sys.executable, "-m", "ml.benchmark", "--child"]
            )
            self.assertEqual(kwargs["timeout"], 45)
            self.assertTrue(kwargs["capture_output"] and kwargs["check"])
            return subprocess.CompletedProcess(command, 0, stdout=encoded(by_id[command[4]]))

        def processor():
            # Linux platform.processor() uses a subprocess. Exercise that boundary
            # on every host without requiring the Unix-only uname executable.
            return subprocess.check_output(
                [sys.executable, "-c", "print('synthetic-processor')"], text=True
            ).strip()

        # Replacing an attribute on benchmark.subprocess would mutate the shared
        # stdlib module and intercept platform.processor()'s unrelated process.
        with patch.object(benchmark, "subprocess") as processes:
            run = processes.run
            run.side_effect = child
            with patch.object(
                benchmark, "admission_probe", new=AsyncMock(return_value=self.report["admission"])
            ):
                with patch.object(
                    benchmark, "default_rate_probe", return_value=self.report["default_rate"]
                ):
                    with patch.object(benchmark.platform, "processor", side_effect=processor):
                        report = benchmark.build_report()
        self.assertEqual(run.call_count, 27)
        self.assertEqual(report["environment"]["processor"], "synthetic-processor")
        benchmark.verify_report(report)

    def test_hard_child_timeout_exits_with_fixed_safe_error(self):
        output = io.StringIO()
        with patch.object(
            benchmark, "build_report", side_effect=subprocess.TimeoutExpired("PRIVATE", 45)
        ):
            with contextlib.redirect_stderr(output):
                self.assertEqual(benchmark.main(["--output", "ml/artifacts/unused.json"]), 1)
        self.assertEqual(output.getvalue(), "benchmark_failed\n")
