"""Reproduce a no-train decision and synthetic mechanics report using the production baseline."""

import argparse
import sys
import time
from pathlib import Path

from ml.audit import AuditError, audit, digest, encoded, parse_json, read_bounded, require
from ml.mechanical_cases import Case, cases

ROOT = Path(__file__).resolve().parent
# The repository's API is not installed as a package. Import its trusted local source only.
sys.path.insert(0, str(ROOT.parent / "api"))
from app.analysis import analyze  # noqa: E402
from app.ingestion import ReviewInputError, validate_submission  # noqa: E402
from app.results import METHODOLOGY_VERSION  # noqa: E402

VERSION = "rt-mechanics-eval-0.1.0"
CODE_FILES = (
    "ml/evaluate.py",
    "ml/mechanical_cases.py",
    "ml/audit.py",
    "api/app/analysis.py",
    "api/app/signals.py",
    "api/app/results.py",
    "api/app/schemas.py",
    "api/app/ingestion.py",
)


def training_decision(catalog: dict) -> dict:
    require(
        isinstance(catalog, dict) and catalog.get("audit_version") == "rt-source-audit-0.1.0",
        "source_review_required",
    )
    sources = catalog.get("sources")
    require(isinstance(sources, list) and bool(sources), "source_review_required")
    identifiers = set()
    for source in sources:
        require(
            isinstance(source, dict) and isinstance(source.get("source_id"), str),
            "source_review_required",
        )
        require(source["source_id"] not in identifiers, "source_review_required")
        identifiers.add(source["source_id"])
        expected = (
            "synthetic_only" if source["source_id"] == "synthetic-fixture-v1" else "not_approved"
        )
        require(
            source.get("admission") == expected and source.get("training_authorized") is False,
            "source_review_required",
        )
    require("synthetic-fixture-v1" in identifiers, "source_review_required")
    return {
        "status": "no_train",
        "trained_model": None,
        "training_authorized": False,
        "reasons": [
            "no_admitted_real_corpus",
            "no_independent_in_domain_target",
            "synthetic_cases_do_not_validate_authenticity",
        ],
        "candidate_status": {s["source_id"]: s["admission"] for s in sources},
    }


def evaluate_case(case: Case) -> dict:
    batch = validate_submission(
        {
            "schema_version": "1",
            "category": "electronics",
            "language": "en",
            "origin": "paste",
            "reviews": case.rows,
        }
    )
    output = analyze(batch, time.monotonic() + 10)
    by_ref = {r.ref: r for r in output.reviews}
    findings = {f.signal_id: f for f in output.findings}
    references_valid, spans_valid = True, True
    for finding in output.findings:
        references_valid &= set(finding.supporting_review_refs) <= by_ref.keys()
        for item in finding.evidence:
            references_valid &= set(item.review_refs) <= by_ref.keys()
            if item.matches:
                if len(item.review_refs) != 1 or item.review_refs[0] not in by_ref:
                    spans_valid = False
                    continue
                text = by_ref[item.review_refs[0]].text
                for match in item.matches:
                    spans_valid &= 0 <= match.start < match.end <= len(text)
                    spans_valid &= (
                        " ".join(text[match.start : match.end].casefold().split()) == match.phrase
                    )
    checks = {
        "score_matches_declared_fixture": output.score.value == case.score,
        "score_status_coherent": output.score.status
        == ("insufficient_evidence" if output.score.value is None else "experimental"),
        "signal_expectations_match": all(
            (
                findings[name].assessment,
                findings[name].matching_review_count,
                findings[name].coverage.eligible,
            )
            == expected
            for name, expected in case.signals.items()
        ),
        "confidence_unset": output.confidence.level is None
        and output.confidence.status == "not_validated",
        "references_resolve": references_valid,
        "matched_spans_resolve": spans_valid,
        "fixed_scoring_panel": set(output.score.evaluated_signal_ids)
        <= {"text_repetition", "incentive_language"},
        "methodology_consistent": all(
            f.methodology_version == output.methodology_version for f in output.findings
        ),
        "unavailable_is_not_zero": all(
            f.value is None and f.coverage.evaluated == 0 and not f.evidence
            for f in output.findings
            if f.assessment == "unavailable"
        ),
    }
    return {
        "case_id": case.case_id,
        "scope": "authored_synthetic_mechanics",
        "rows": output.review_count,
        "score": output.score.model_dump(),
        "signals": {
            f.signal_id: {
                "assessment": f.assessment,
                "matching_reviews": f.matching_review_count,
                "coverage": f.coverage.model_dump(),
                "availability_reason": f.availability_reason,
                "value": f.value.model_dump() if f.value is not None else None,
            }
            for f in output.findings
        },
        "redactions": output.coverage.redactions,
        "checks": checks,
        "passed": all(checks.values()),
        "limitation": case.limitation,
    }


def build_report() -> dict:
    catalog = parse_json((ROOT / "sources.json").read_bytes())
    decision = training_decision(catalog)
    # Verify the Step 7 freeze but never fit/tune on its labels or holdout membership.
    source = next(s for s in catalog["sources"] if s["source_id"] == "synthetic-fixture-v1")
    frozen = parse_json((ROOT / "fixtures/synthetic.manifest.json").read_bytes())
    current = audit(read_bounded(ROOT / "fixtures/synthetic.jsonl"), source)
    require(current == frozen, "audit_manifest_mismatch")
    scenario_rows = [evaluate_case(case) for case in cases()]
    indexed = {case["case_id"]: case for case in scenario_rows}
    relations = {
        "metadata_removal_preserves_score": indexed["contextual_launch_and_ratings"]["score"]
        == indexed["metadata_removed"]["score"],
        "masking_case_counts_contacts": indexed["masked_contact_collision"]["redactions"]["email"]
        == 20,
        "feature_overflow_withholds": indexed["feature_limit"]["signals"]["text_repetition"][
            "availability_reason"
        ]
        == "feature_limit",
    }
    report = {
        "evaluation_version": VERSION,
        "methodology_version": METHODOLOGY_VERSION,
        "scope": "synthetic_mechanics_only",
        "training_decision": decision,
        "catalog_sha256": digest(encoded(catalog)),
        "audit_manifest_sha256": frozen["manifest_sha256"],
        "code_hash_policy": "UTF-8 source bytes with CRLF normalized to LF",
        "implementation_sha256": {
            name: digest((ROOT.parent / name).read_bytes().replace(b"\r\n", b"\n"))
            for name in CODE_FILES
        },
        "supervised_metrics": {
            "status": "not_available",
            "reason": "no_independent_admitted_target",
            "precision": None,
            "recall": None,
            "f1": None,
            "confusion_matrix": None,
            "calibration": None,
        },
        "cases": scenario_rows,
        "relations": relations,
        "cases_total": len(scenario_rows),
        "cases_passed": sum(c["passed"] for c in scenario_rows),
        "passed": all(c["passed"] for c in scenario_rows) and all(relations.values()),
        "limitations": [
            "Fixture agreement is not classifier accuracy or independent validation.",
            "No learned model, probability calibration or confidence level is justified.",
            "Full resource benchmarks and release decisions remain later roadmap gates.",
        ],
    }
    report["report_sha256"] = digest(encoded(report))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report()
        if args.verify:
            # Compare through the same strict JSON decoder so decimal fractions round-trip.
            require(
                parse_json(read_bounded(args.verify)) == parse_json(encoded(report)),
                "evaluation_report_mismatch",
            )
        else:
            target = args.output.resolve()
            require(
                target.is_relative_to((ROOT / "artifacts").resolve()), "output_outside_artifacts"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as handle:
                handle.write(encoded(report) + b"\n")
        print("mechanics_passed no_train" if report["passed"] else "mechanics_failed")
        return 0 if report["passed"] else 1
    except AuditError as error:
        print(str(error), file=sys.stderr)
    except (OSError, ReviewInputError, ValueError, KeyError, TypeError, RuntimeError):
        print("evaluation_failed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
