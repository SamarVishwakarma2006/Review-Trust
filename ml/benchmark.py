"""Synthetic-only resource and sampling benchmark; no training or accuracy claims."""

import argparse
import asyncio
import csv
import ctypes
import io
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from ml import evaluate
from ml.audit import AuditError, digest, encoded, read_bounded, require, unique_object
from ml.mechanical_cases import distinct

# evaluate inserts the trusted repository API directory, matching the offline evaluator.
# isort: off
from app.main import create_app  # noqa: E402
from app.security import Settings  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
# isort: on

ROOT = Path(__file__).resolve().parent.parent
VERSION = "rt-resource-benchmark-0.1.0"
LIMIT = 1_048_576
CASE_IDS = (
    "small_20",
    "dense_500",
    "aggregate_250000",
    "single_5000",
    "json_exact_1mib",
    "csv_500_unicode",
    "over_1mib",
    "feature_limit",
    "unicode_expansion",
)
CODE_FILES = (
    *evaluate.CODE_FILES,
    "ml/benchmark.py",
    "api/app/main.py",
    "api/app/security.py",
    "api/app/uploads.py",
    "api/requirements.txt",
    "api/requirements-dev.txt",
)


def request_case(case_id):
    """Fixed authored workloads; return exact bytes, route, media type and expected status."""
    require(case_id in CASE_IDS, "unknown_benchmark_case")
    rows = distinct()
    if case_id == "dense_500":
        shared = " ".join(f"feature{i}" for i in range(45))
        rows = [{"text": f"{shared} variant{i}"} for i in range(500)]
    elif case_id == "aggregate_250000":
        rows = [{"text": ("screen battery display audio button " * 15)[:500]}] * 500
    elif case_id == "single_5000":
        rows = [{"text": ("screen battery display audio button " * 150)[:5000]}]
    elif case_id == "feature_limit":
        rows = [{"text": " ".join(f"w{i}term{j}" for j in range(300))} for i in range(40)]
    elif case_id == "unicode_expansion":
        # NFKC expands each U+FDFA to eighteen code points. It is declared English,
        # exposing that the declaration is not language detection.
        rows = [{"text": "ﷺ" * 500}] * 500
    payload = {
        "schema_version": "1",
        "category": "electronics",
        "language": "en",
        "origin": "paste",
        "reviews": rows,
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    route, media = "/v1/analyze", "application/json"
    if case_id == "csv_500_unicode":
        prefix_text = "screen battery display audio button "
        rows = [{"text": prefix_text + "😀" * (500 - len(prefix_text))}] * 500
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["text"])
        writer.writerows([row["text"]] for row in rows)
        parts = []
        for name, value in (
            ("schema_version", "1"),
            ("category", "electronics"),
            ("language", "en"),
        ):
            parts.append(
                f'--bench\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'
            )
        prefix = (
            "".join(parts) + '--bench\r\nContent-Disposition: form-data; name="file"; '
            'filename="synthetic.csv"\r\nContent-Type: text/csv\r\n\r\n'
        ).encode()
        suffix = b"\r\n--bench--\r\n"
        content = stream.getvalue().encode()
        body = prefix + content + suffix
        route, media = "/v1/analyze/csv", "multipart/form-data; boundary=bench"
    elif case_id in {"json_exact_1mib", "over_1mib"}:
        body += b" " * (LIMIT - len(body) + (case_id == "over_1mib"))
    return body, route, media, 413 if case_id == "over_1mib" else 200


def peak_rss():
    """Process lifetime resident high-water mark, not allocation delta or host RAM."""
    if sys.platform == "win32":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in ("peak", "working", "qpp", "qpu", "qnp", "qnu", "page", "peakpage")
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        ]
        if not psapi.GetProcessMemoryInfo(
            kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
        ):
            return None
        return counters.peak
    if sys.platform.startswith("linux") or sys.platform == "darwin":
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value * (1 if sys.platform == "darwin" else 1024))
    return None


def measure(case_id):
    body, route, media, expected = request_case(case_id)
    # Exclude imports, app/client setup and workload construction. Include transport
    # bridge, request validation, production worker, masking, analysis and serialization.
    with TestClient(create_app(Settings()), raise_server_exceptions=False) as client:
        cpu, wall = time.process_time(), time.perf_counter()
        response = client.post(route, content=body, headers={"Content-Type": media})
        wall, cpu = time.perf_counter() - wall, time.process_time() - cpu
        result = response.json()
    code = result.get("error", {}).get("code")
    return {
        "case_id": case_id,
        "input_sha256": digest(body),
        "input_bytes": len(body),
        "status": response.status_code,
        "expected_status": expected,
        "error_code": code,
        "wall_seconds": wall,
        "cpu_seconds": cpu,
        "peak_rss_bytes": peak_rss(),
        "response_bytes": len(response.content),
        "score": result.get("score", {}).get("value"),
        "confidence_unset": result.get("confidence", {}).get("level") is None,
        "availability": {f["signal_id"]: f["assessment"] for f in result.get("findings", [])},
        "passed": response.status_code == expected,
    }


def sampling_report():
    template = [{"text": "This supplied template describes the screen battery and audio."}] * 20
    whole = template + distinct()
    rng = random.Random(20261028)
    samples = {
        "whole_40": whole,
        "first_20": whole[:20],
        "last_20": whole[20:],
        "seeded_20": rng.sample(whole, 20),
        "short_19": whole[20:39],
        "low_coverage": whole[20:] + [{"text": "ok"}] * 6,
    }
    report = []
    for name, rows in samples.items():
        body = encoded(
            {
                "schema_version": "1",
                "category": "electronics",
                "language": "en",
                "origin": "paste",
                "reviews": rows,
            }
        )
        result = evaluate.analyze(
            evaluate.validate_submission(json.loads(body)), time.monotonic() + 10
        )
        report.append(
            {
                "case_id": name,
                "input_sha256": digest(body),
                "rows": len(rows),
                "score": result.score.value,
            }
        )
    values = {row["case_id"]: row["score"] for row in report}
    require(
        values["whole_40"] == 50 and values["first_20"] == 0 and values["last_20"] == 100,
        "sampling_expectation_failed",
    )
    require(
        values["short_19"] is None and values["low_coverage"] is None, "coverage_expectation_failed"
    )
    return {"seed": 20261028, "cases": report, "passed": True}


def summarize(samples):
    require(bool(samples), "missing_samples")
    return {
        "wall_median_seconds": statistics.median(s["wall_seconds"] for s in samples),
        "wall_max_seconds": max(s["wall_seconds"] for s in samples),
        "cpu_median_seconds": statistics.median(s["cpu_seconds"] for s in samples),
        "peak_rss_max_bytes": max(
            (s["peak_rss_bytes"] for s in samples if s["peak_rss_bytes"] is not None), default=None
        ),
        "passed": all(s["passed"] for s in samples),
    }


async def exchange(app, body, gate=None, delay=0, path="/v1/analyze"):
    messages = []

    async def receive():
        if gate is not None:
            await gate.wait()
        await asyncio.sleep(delay)
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    started = time.perf_counter()
    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET" if path == "/health" else "POST",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "server": ("benchmark", 80),
            "client": ("203.0.113.1", 1234),
            "headers": [(b"content-type", b"application/json")],
        },
        receive,
        send,
    )
    status = next(m["status"] for m in messages if m["type"] == "http.response.start")
    response = json.loads(
        b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
    )
    return {
        "status": status,
        "error_code": response.get("error", {}).get("code"),
        "wall_seconds": time.perf_counter() - started,
    }


async def admission_probe():
    # A receive barrier guarantees occupied slots without timing-dependent sleeps.
    # Rate override isolates admission; measure default rate separately below.
    app = create_app(Settings(rate_per_minute=600, rate_burst=100))
    gate = asyncio.Event()
    body = request_case("dense_500")[0]
    tasks = [asyncio.create_task(exchange(app, body, gate)) for _ in range(2)]
    try:
        async with asyncio.timeout(5):
            while app.state.controls.active < 2:
                await asyncio.sleep(0.001)
        rejected = await exchange(app, body)
        health = await exchange(app, b"", path="/health")
    finally:
        gate.set()
        completed = await asyncio.gather(*tasks)
    slow = create_app(Settings(timeout_seconds=0.01))
    timeout = await exchange(slow, b"{}", delay=0.03)
    passed = (
        [r["status"] for r in completed] == [200, 200]
        and rejected["status"] == 503
        and rejected["error_code"] == "analysis_busy"
        and health["status"] == 200
        and app.state.controls.active == 0
        and timeout["status"] == 503
        and timeout["error_code"] == "request_timeout"
        and slow.state.controls.active == 0
    )
    return {
        "settings": app.state.settings.model_dump(),
        "barrier_controlled": True,
        "two_dense_requests": completed,
        "third_request": rejected,
        "health": health,
        "active_after": app.state.controls.active,
        "slow_body": timeout,
        "slow_timeout_seconds": 0.01,
        "slow_receive_delay_seconds": 0.03,
        "slow_active_after": slow.state.controls.active,
        "passed": passed,
    }


def default_rate_probe():
    with TestClient(create_app(Settings())) as client:
        body, route, media, _ = request_case("small_20")
        statuses = [
            client.post(route, content=body, headers={"Content-Type": media}).status_code
            for _ in range(3)
        ]
    return {"statuses": statuses, "passed": statuses == [200, 200, 429]}


def implementation_hashes():
    return {name: digest((ROOT / name).read_bytes().replace(b"\r\n", b"\n")) for name in CODE_FILES}


def build_report():
    implementation = implementation_hashes()
    mechanics = evaluate.build_report()
    require(mechanics["passed"], "mechanics_failed")
    results = []
    for case_id in CASE_IDS:
        samples = []
        for _ in range(3):
            child = subprocess.run(
                [sys.executable, "-m", "ml.benchmark", "--child", case_id],
                cwd=ROOT,
                capture_output=True,
                timeout=45,
                check=True,
            )
            samples.append(json.loads(child.stdout))
        results.append({"case_id": case_id, "samples": samples, "summary": summarize(samples)})
    admission, rate = asyncio.run(admission_probe()), default_rate_probe()
    report = {
        "benchmark_version": VERSION,
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "environment": {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
            "logical_cpus": os.cpu_count(),
            "python": platform.python_version(),
            "packages": {
                name: version(name)
                for name in (
                    "fastapi",
                    "pydantic",
                    "starlette",
                    "httpx2",
                    "anyio",
                    "python-multipart",
                    "uvicorn",
                )
            },
        },
        "settings": Settings().model_dump(),
        "measurement": (
            "Three fresh child processes per case; timed TestClient POST only; lifetime process "
            "peak RSS includes imports/fixture/client; no network or provider latency."
        ),
        "baseline_comparison": None,
        "implementation_sha256": implementation,
        "mechanics_report_sha256": mechanics["report_sha256"],
        "mechanics_cases_passed": mechanics["cases_passed"],
        "sampling": sampling_report(),
        "resources": results,
        "admission": admission,
        "default_rate": rate,
        "training_decision": mechanics["training_decision"],
        "supervised_metrics": mechanics["supervised_metrics"],
        "public_numeric_score_decision": "not_approved_withhold_before_public_release",
        "passed": all(case["summary"]["passed"] for case in results)
        and admission["passed"]
        and rate["passed"],
    }
    require(implementation == implementation_hashes(), "implementation_changed_during_measurement")
    report["report_sha256"] = digest(encoded(report))
    return report


def write_report(target, report):
    target = target.resolve()
    require(target.is_relative_to((ROOT / "ml/artifacts").resolve()), "output_outside_artifacts")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(encoded(report) + b"\n")


def verify_report(report):
    """Verify a measurement record, not replay noisy timings or certify performance."""
    stored = dict(report)
    checksum = stored.pop("report_sha256")
    require(digest(encoded(stored)) == checksum, "benchmark_checksum_mismatch")
    require(report["benchmark_version"] == VERSION and report["passed"], "benchmark_failed")
    require(set(report["implementation_sha256"]) == set(CODE_FILES), "implementation_set_changed")
    for name, checksum in report["implementation_sha256"].items():
        require(
            digest((ROOT / name).read_bytes().replace(b"\r\n", b"\n")) == checksum,
            "implementation_changed",
        )
    require(
        [case["case_id"] for case in report["resources"]] == list(CASE_IDS),
        "benchmark_cases_changed",
    )
    for case in report["resources"]:
        body, _, _, status = request_case(case["case_id"])
        require(len(case["samples"]) == 3, "missing_samples")
        for sample in case["samples"]:
            require(
                sample["input_sha256"] == digest(body) and sample["input_bytes"] == len(body),
                "benchmark_input_changed",
            )
            require(
                sample["status"] == status and sample["passed"] and sample["confidence_unset"],
                "benchmark_outcome_changed",
            )
            for metric in ("wall_seconds", "cpu_seconds"):
                value = sample[metric]
                require(
                    type(value) in (int, float) and math.isfinite(value) and value >= 0,
                    "invalid_measurement",
                )
            require(sample["wall_seconds"] > 0, "invalid_measurement")
            rss = sample["peak_rss_bytes"]
            require(rss is None or (type(rss) is int and rss > 0), "invalid_memory_measurement")
        require(case["summary"] == summarize(case["samples"]), "benchmark_summary_changed")
    mechanics = evaluate.build_report()
    require(report["mechanics_report_sha256"] == mechanics["report_sha256"], "mechanics_changed")
    require(report["sampling"] == sampling_report(), "sampling_changed")
    require(
        report["training_decision"] == mechanics["training_decision"]
        and report["supervised_metrics"] == mechanics["supervised_metrics"],
        "target_changed",
    )
    require(
        report["public_numeric_score_decision"] == "not_approved_withhold_before_public_release",
        "release_decision_changed",
    )
    require(report["admission"]["passed"] and report["default_rate"]["passed"], "probe_failed")
    probe = report["admission"]
    require(
        [r["status"] for r in probe["two_dense_requests"]] == [200, 200]
        and probe["third_request"]["status"] == 503
        and probe["third_request"]["error_code"] == "analysis_busy"
        and probe["health"]["status"] == 200
        and probe["active_after"] == 0
        and probe["slow_body"]["status"] == 503
        and probe["slow_body"]["error_code"] == "request_timeout"
        and probe["slow_active_after"] == 0
        and report["default_rate"]["statuses"] == [200, 200, 429],
        "probe_outcome_changed",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    action.add_argument("--child", choices=CASE_IDS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.child:
            print(json.dumps(measure(args.child), separators=(",", ":")))
            return 0
        if args.verify:
            verify_report(json.loads(read_bounded(args.verify), object_pairs_hook=unique_object))
            print("benchmark_record_verified no_train")
            return 0
        report = build_report()
        write_report(args.output, report)
        print("benchmark_passed no_train" if report["passed"] else "benchmark_failed")
        return 0 if report["passed"] else 1
    except (AuditError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        print("benchmark_failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
