"""Synthetic-only evaluation integrity and no-train gates, not model accuracy tests."""

import contextlib
import copy
import io
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ml import evaluate
from ml.audit import AuditError, encoded, parse_json
from ml.mechanical_cases import cases


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evaluate.build_report()
        cls.catalog = parse_json((evaluate.ROOT / "sources.json").read_bytes())

    def test_report_reproduces_declared_mechanics_without_supervised_metrics(self):
        report = self.report
        self.assertTrue(report["passed"])
        self.assertEqual(report["cases_total"], 17)
        self.assertEqual(report["cases_passed"], 17)
        self.assertTrue(all(report["relations"].values()))
        self.assertEqual(report["training_decision"]["status"], "no_train")
        self.assertFalse(report["training_decision"]["training_authorized"])
        self.assertIsNone(report["training_decision"]["trained_model"])
        for key in ("precision", "recall", "f1", "confusion_matrix", "calibration"):
            self.assertIsNone(report["supervised_metrics"][key])
        serialized = encoded(report).decode()
        self.assertNotIn("contact0@example.invalid", serialized)
        self.assertNotIn(str(evaluate.ROOT), serialized)
        self.assertNotIn('"reviews":', serialized)
        self.assertEqual(report, evaluate.build_report())

    def test_no_train_decision_cannot_be_overridden_by_a_permission_flag(self):
        for mutate in (
            lambda c: c["sources"][1].update(training_authorized=True),
            lambda c: c["sources"][1].update(admission="approved"),
            lambda c: c.update(sources=[]),
            lambda c: c.update(audit_version="unknown"),
            lambda c: c["sources"].append(c["sources"][0]),
        ):
            with self.subTest(mutate=mutate):
                changed = copy.deepcopy(self.catalog)
                mutate(changed)
                with self.assertRaisesRegex(AuditError, "source_review_required"):
                    evaluate.training_decision(changed)

    def test_case_expectation_mismatch_is_reported_as_failure(self):
        case = replace(cases()[0], score=99)
        output = evaluate.evaluate_case(case)
        self.assertFalse(output["passed"])
        self.assertFalse(output["checks"]["score_matches_declared_fixture"])
        self.assertEqual(output["score"]["value"], 100)

    def test_bad_evidence_and_confidence_cannot_pass_the_report_checks(self):
        case = next(c for c in cases() if c.case_id == "negated_incentive")
        batch = evaluate.validate_submission(
            {
                "schema_version": "1",
                "category": "electronics",
                "language": "en",
                "origin": "paste",
                "reviews": case.rows,
            }
        )
        actual = evaluate.analyze(batch, time.monotonic() + 10)
        actual.findings[1].evidence[0].review_refs = ["r999"]
        actual.confidence = actual.confidence.model_copy(update={"level": "high"})
        with patch.object(evaluate, "analyze", return_value=actual):
            output = evaluate.evaluate_case(case)
        self.assertFalse(output["passed"])
        self.assertFalse(output["checks"]["references_resolve"])
        self.assertFalse(output["checks"]["matched_spans_resolve"])
        self.assertFalse(output["checks"]["confidence_unset"])

    def test_changed_audit_freeze_stops_before_production_analysis(self):
        with (
            patch.object(evaluate, "audit", return_value={"changed": True}),
            patch.object(evaluate, "analyze") as analyzer,
        ):
            with self.assertRaisesRegex(AuditError, "audit_manifest_mismatch"):
                evaluate.build_report()
            analyzer.assert_not_called()

    def test_cli_create_verify_no_overwrite_and_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "artifacts/report.json"
            with (
                patch.object(evaluate, "ROOT", root),
                patch.object(evaluate, "build_report", return_value=self.report),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(evaluate.main(["--output", str(target)]), 0)
                frozen = target.read_bytes()
                self.assertEqual(evaluate.main(["--verify", str(target)]), 0)
                self.assertEqual(evaluate.main(["--output", str(target)]), 1)
                self.assertEqual(target.read_bytes(), frozen)
                self.assertEqual(evaluate.main(["--output", str(root / "outside.json")]), 1)
                self.assertFalse((root / "outside.json").exists())
                changed = copy.deepcopy(self.report)
                changed["supervised_metrics"]["precision"] = 1
                target.write_bytes(encoded(changed))
                self.assertEqual(evaluate.main(["--verify", str(target)]), 1)

    def test_unexpected_failure_is_safe_and_failed_checks_return_nonzero(self):
        output = io.StringIO()
        with (
            patch.object(evaluate, "build_report", side_effect=RuntimeError("PRIVATE_REVIEW")),
            contextlib.redirect_stderr(output),
        ):
            self.assertEqual(evaluate.main(["--verify", "PRIVATE_PATH"]), 1)
        self.assertEqual(output.getvalue(), "evaluation_failed\n")
        failed = self.report | {"passed": False}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with (
                patch.object(evaluate, "ROOT", root),
                patch.object(evaluate, "build_report", return_value=failed),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(
                    evaluate.main(["--output", str(root / "artifacts/failed.json")]), 1
                )

    def test_committed_mechanical_reference_matches_current_implementation(self):
        frozen = parse_json((evaluate.ROOT / "fixtures/mechanics.expected.json").read_bytes())
        self.assertEqual(parse_json(encoded(self.report)), frozen)


if __name__ == "__main__":
    unittest.main()
