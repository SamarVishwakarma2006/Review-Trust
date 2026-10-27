"""Synthetic-only checks for admission, labels, grouping, manifests and safe failures."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ml import audit as pipeline

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic.jsonl"
SOURCE = {"source_id": "synthetic-fixture-v1", "admission": "synthetic_only"}


def data(rows):
    return b"\n".join(pipeline.encoded(r) for r in rows) + b"\n"


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.raw = FIXTURE.read_bytes()
        self.rows = pipeline.load_records(self.raw)

    def test_fixture_freezes_all_rows_and_has_no_cross_partition_product_or_text_groups(self):
        report = pipeline.audit(self.raw, SOURCE)
        self.assertEqual(report["rows"], 24)
        self.assertFalse(report["training_authorized"])
        self.assertEqual(report["target"], "synthetic_scenario_only")
        by_id = {r["record_id"]: r for r in report["assignments"]}
        products, exacts = {}, {}
        for row in self.rows:
            assigned = by_id[row["record_id"]]["partition"]
            for table, key in (
                (products, row["product_group"]),
                (exacts, pipeline.normalized(row["text"])),
            ):
                if key in table:
                    self.assertEqual(table[key], assigned)
                table[key] = assigned
        self.assertEqual(report["duplicates"]["exact_pairs"], 1)
        self.assertEqual(report["largest_group"], 4)
        self.assertEqual(sum(p["rows"] for p in report["partitions"].values()), 24)
        self.assertTrue(all(p["rows"] > 0 for p in report["partitions"].values()))
        self.assertEqual(report["quality"]["missing_rating"], 8)
        self.assertEqual(report["quality"]["missing_timestamp"], 6)
        self.assertEqual(report["label_counts"], {"deceptive": 12, "non_deceptive": 12})
        # Hashes and counts only: no review bodies, source product IDs or evidence payloads.
        text = json.dumps(report)
        self.assertNotIn(self.rows[0]["text"], text)
        self.assertNotIn(self.rows[0]["product_group"], text)
        self.assertNotIn('"votes"', text)

    def test_repeatability_order_independence_and_annotation_blind_assignment(self):
        original = pipeline.audit(self.raw, SOURCE)
        self.assertEqual(original, pipeline.audit(self.raw, SOURCE))
        changed = pipeline.audit(data(list(reversed(self.rows))), SOURCE)
        self.assertEqual(original["assignments"], changed["assignments"])
        rows = copy.deepcopy(self.rows)
        for row in rows:
            row["votes"] = []
        relabelled = pipeline.audit(data(rows), SOURCE)
        self.assertEqual(
            [(r["record_id"], r["partition"]) for r in original["assignments"]],
            [(r["record_id"], r["partition"]) for r in relabelled["assignments"]],
        )
        self.assertNotEqual(original["manifest_sha256"], relabelled["manifest_sha256"])

    def test_transitive_near_duplicates_merge_products_and_short_text_is_exact_only(self):
        rows = copy.deepcopy(self.rows[:3])
        words = [f"token{i}" for i in range(20)]
        for i, row in enumerate(rows):
            row["text"] = " ".join(words + [f"extra{j}" for j in range(i * 4)])
            row["product_group"] = row["record_id"]
        groups, counts = pipeline.components(rows)
        self.assertEqual(len(groups), 1)
        self.assertEqual(counts, {"exact_pairs": 0, "near_pairs": 2})
        rows[0]["text"], rows[1]["text"], rows[2]["text"] = "Good!", "ＧＯＯＤ", "Good device"
        groups, counts = pipeline.components(rows)
        self.assertEqual(sorted(map(len, groups)), [1, 2])
        self.assertEqual(counts["exact_pairs"], 1)

    def test_near_match_threshold_is_inclusive_without_float_rounding(self):
        rows = copy.deepcopy(self.rows[:2])
        for row in rows:
            row["product_group"] = row["record_id"]
        rows[0]["text"] = "a b c d e f"
        rows[1]["text"] = "a b c d e f g"
        groups, counts = pipeline.components(rows)
        self.assertEqual(counts["near_pairs"], 1)  # 4/5 trigram Jaccard = exactly .80.
        self.assertEqual(len(groups), 1)
        rows[1]["text"] += " h"
        self.assertEqual(pipeline.components(rows)[1]["near_pairs"], 0)

    def test_large_components_are_diagnosed_without_splitting_them_or_rerolling_seed(self):
        rows = copy.deepcopy(self.rows)
        for row in rows:
            row["product_group"] = "a" * 64
        report = pipeline.audit(data(rows), SOURCE)
        self.assertEqual(report["groups"], 1)
        self.assertEqual(report["largest_group"], 24)
        self.assertIn("empty_partition", report["partition_diagnostics"])
        self.assertEqual(len({r["partition"] for r in report["assignments"]}), 1)

    def test_scope_and_product_missingness_is_explicit(self):
        row = self.rows[0] | {"product_group": None, "category": "unknown", "language": "other"}
        report = pipeline.audit(data([row]), SOURCE)
        self.assertEqual(report["quality"]["missing_product_group"], 1)
        self.assertIn("incomplete_scope_or_product_groups", report["partition_diagnostics"])
        self.assertFalse(report["training_authorized"])

    def test_labels_require_independent_unanimous_documented_votes(self):
        votes = copy.deepcopy(self.rows[0]["votes"])
        decision = votes[0]["decision"]
        self.assertEqual(pipeline.resolve_label(votes, synthetic=True), decision)
        for basis in ("sentiment_proxy", "platform_proxy", "unknown", "external_documentation"):
            changed = [v | {"basis": basis} for v in votes]
            self.assertEqual(pipeline.resolve_label(changed, synthetic=True), "unknown")
        for changed in (
            votes[:1],
            votes + [votes[0] | {"annotator": "a3", "decision": "unknown"}],
            [votes[0], votes[1] | {"decision": "unknown"}],
            [votes[0], votes[1] | {"evidence_ref": None}],
        ):
            self.assertEqual(pipeline.resolve_label(changed, synthetic=True), "unknown")
        conflict = "deceptive" if decision == "non_deceptive" else "non_deceptive"
        self.assertEqual(
            pipeline.resolve_label([votes[0], votes[1] | {"decision": conflict}], True), "unknown"
        )

    def test_duplicate_annotator_and_unknown_fields_are_rejected(self):
        row = copy.deepcopy(self.rows[0])
        row["votes"][1]["annotator"] = row["votes"][0]["annotator"]
        with self.assertRaisesRegex(pipeline.AuditError, "invalid_annotator"):
            pipeline.load_records(data([row]))
        with self.assertRaisesRegex(pipeline.AuditError, "invalid_record_fields"):
            pipeline.load_records(data([self.rows[0] | {"PRIVATE_FIELD": "PRIVATE_BODY"}]))
        with self.assertRaisesRegex(pipeline.AuditError, "duplicate_record_id"):
            pipeline.load_records(data([self.rows[0], self.rows[0]]))

    def test_invalid_json_limits_unicode_and_decimal_rating_boundaries(self):
        for raw in (b"{}\n\n", b'{"text":1,"text":2}', b"NaN", b"\xff"):
            with self.subTest(raw=raw):
                with self.assertRaises(pipeline.AuditError):
                    pipeline.load_records(raw)
        for changes in (
            {"text": " "},
            {"text": "x" * 5001},
            {"text": "\ud800"},
            {"rating": True},
            {"rating": 0},
            {"timestamp": "2020-02-30"},
            {"product_group": "unhashed"},
            {
                "votes": [
                    {"annotator": "a1", "decision": [], "basis": "unknown", "evidence_ref": None}
                ]
            },
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(pipeline.AuditError):
                    pipeline.load_records(data([self.rows[0] | changes]))
        raw = data([self.rows[0] | {"rating": 5}]).replace(
            b'"rating":5', b'"rating":5.00000000000000000001'
        )
        with self.assertRaisesRegex(pipeline.AuditError, "invalid_rating"):
            pipeline.load_records(raw)
        with patch.object(pipeline, "MAX_ROWS", 1):
            with self.assertRaisesRegex(pipeline.AuditError, "input_row_limit"):
                pipeline.load_records(self.raw)
        with patch.object(pipeline, "MAX_BYTES", 1):
            with self.assertRaisesRegex(pipeline.AuditError, "input_byte_limit"):
                pipeline.load_records(self.raw)

    def test_conflicts_are_counted_and_aggregate_text_is_not_silently_dropped(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["votes"][0]["decision"] = "deceptive"
        rows[0]["votes"][1]["decision"] = "non_deceptive"
        report = pipeline.audit(data(rows), SOURCE)
        self.assertEqual(report["quality"]["conflicting_vote_rows"], 1)
        self.assertEqual(report["quality"]["unknown_labels"], 1)
        with patch.object(pipeline, "MAX_ROWS", 100):
            rows = [copy.deepcopy(self.rows[0]) for _ in range(51)]
            for i, row in enumerate(rows):
                row["record_id"] = pipeline.digest(str(i).encode())
                row["text"] = "x" * 5000
            with self.assertRaisesRegex(pipeline.AuditError, "aggregate_text_limit"):
                pipeline.load_records(data(rows))

    def test_committed_synthetic_manifest_matches_current_code_card_and_bytes(self):
        card = next(
            s
            for s in pipeline.parse_json((FIXTURE.parents[1] / "sources.json").read_bytes())[
                "sources"
            ]
            if s["source_id"] == "synthetic-fixture-v1"
        )
        expected = pipeline.parse_json(FIXTURE.with_name("synthetic.manifest.json").read_bytes())
        self.assertEqual(pipeline.audit(self.raw, card), expected)
        for mutated in (
            self.raw.replace(b"2020-01-01", b"2020-01-02", 1),
            data([self.rows[0] | {"text": "Changed synthetic text"}] + self.rows[1:]),
        ):
            self.assertNotEqual(
                pipeline.audit(mutated, card)["manifest_sha256"], expected["manifest_sha256"]
            )

    def test_cli_denies_unapproved_source_before_opening_data(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output), patch.object(pipeline, "read_bounded") as reader:
            code = pipeline.main(
                ["--source", "yelpchi", "--records", "PRIVATE_PATH", "--output", "out.json"]
            )
        self.assertEqual(code, 1)
        reader.assert_not_called()
        self.assertEqual(output.getvalue(), "source_not_admitted\n")

    def test_cli_freeze_verify_tamper_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            root.joinpath("sources.json").write_bytes(pipeline.encoded({"sources": [SOURCE]}))
            raw = root / "records.jsonl"
            raw.write_bytes(self.raw)
            output = root / "artifacts" / "manifest.json"
            base = ["--source", "synthetic-fixture-v1", "--records", str(raw)]
            with (
                patch.object(pipeline, "ROOT", root),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(pipeline.main(base + ["--output", str(output)]), 0)
                frozen = output.read_bytes()
                self.assertEqual(pipeline.main(base + ["--verify", str(output)]), 0)
                self.assertEqual(pipeline.main(base + ["--output", str(output)]), 1)
                self.assertEqual(output.read_bytes(), frozen)
                raw.write_bytes(self.raw + b"\n")
                self.assertEqual(pipeline.main(base + ["--verify", str(output)]), 1)
                raw.write_bytes(data([self.rows[0] | {"rating": 1}] + self.rows[1:]))
                self.assertEqual(pipeline.main(base + ["--verify", str(output)]), 1)
                self.assertEqual(pipeline.main(base + ["--output", str(root / "leak.json")]), 1)
                self.assertFalse((root / "leak.json").exists())


if __name__ == "__main__":
    unittest.main()
