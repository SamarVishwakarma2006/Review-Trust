"""Offline audit/split mechanics. Local reviewed inputs only; never train or fetch data."""

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

VERSION = "rt-audit-split-0.1.0"
SEED = 20261027
MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 500
HASH = re.compile(r"[a-f0-9]{64}")
WORDS = re.compile(r"[^\W_]+")
ROOT = Path(__file__).resolve().parent
FIELDS = {
    "record_id",
    "product_group",
    "text",
    "rating",
    "timestamp",
    "category",
    "language",
    "votes",
}
VOTE_FIELDS = {"annotator", "decision", "basis", "evidence_ref"}
DECISIONS = {"deceptive", "non_deceptive", "unknown"}
BASES = {
    "synthetic_scenario",
    "external_documentation",
    "sentiment_proxy",
    "platform_proxy",
    "unknown",
}


class AuditError(ValueError):
    """Fixed public error codes only; no input values or raw body diagnostics."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AuditError(code)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate_json_key")
        value[key] = item
    return value


def invalid_constant(_):
    raise AuditError("invalid_json_number")


def parse_json(data: bytes):
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_float=Decimal,
            parse_constant=invalid_constant,
        )
    except (UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, AuditError):
            raise
        raise AuditError("invalid_json") from None


def resolve_label(votes: list[dict], synthetic: bool) -> str:
    """Unanimous independent supported votes only. Proxies/abstentions cannot become targets."""
    basis = "synthetic_scenario" if synthetic else "external_documentation"
    if (
        len(votes) < 2
        or len({v["annotator"] for v in votes}) != len(votes)
        or any(
            v["basis"] != basis or v["decision"] == "unknown" or v["evidence_ref"] is None
            for v in votes
        )
    ):
        return "unknown"
    decisions = {v["decision"] for v in votes}
    return next(iter(decisions)) if len(decisions) == 1 else "unknown"


def validate_record(row: object) -> dict:
    require(isinstance(row, dict) and set(row) == FIELDS, "invalid_record_fields")
    require(
        isinstance(row["record_id"], str) and HASH.fullmatch(row["record_id"]) is not None,
        "invalid_record_id",
    )
    product = row["product_group"]
    require(
        product is None or isinstance(product, str) and HASH.fullmatch(product) is not None,
        "invalid_product_group",
    )
    text = row["text"]
    require(
        isinstance(text, str)
        and bool(text.strip())
        and len(text) <= 5000
        and "\0" not in text
        and not any(0xD800 <= ord(c) <= 0xDFFF for c in text),
        "invalid_text",
    )
    require(row["category"] in ("electronics", "other", "unknown"), "invalid_category")
    require(row["language"] in ("en", "other", "unknown"), "invalid_language")
    rating = row["rating"]
    require(
        rating is None
        or type(rating) in (int, float, Decimal)
        and 1 <= rating <= 5
        and math.isfinite(rating),
        "invalid_rating",
    )
    timestamp = row["timestamp"]
    if timestamp is not None:
        require(
            isinstance(timestamp, str)
            and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", timestamp) is not None,
            "invalid_timestamp",
        )
        try:
            date.fromisoformat(timestamp)
        except ValueError:
            raise AuditError("invalid_timestamp") from None
    votes = row["votes"]
    require(isinstance(votes, list) and len(votes) <= 3, "invalid_votes")
    annotators = set()
    for vote in votes:
        require(isinstance(vote, dict) and set(vote) == VOTE_FIELDS, "invalid_vote_fields")
        annotator = vote["annotator"]
        require(
            isinstance(annotator, str)
            and re.fullmatch(r"a[1-9][0-9]{0,3}", annotator) is not None
            and annotator not in annotators,
            "invalid_annotator",
        )
        annotators.add(annotator)
        require(
            isinstance(vote["decision"], str)
            and vote["decision"] in DECISIONS
            and isinstance(vote["basis"], str)
            and vote["basis"] in BASES,
            "invalid_vote",
        )
        reference = vote["evidence_ref"]
        require(
            reference is None
            or isinstance(reference, str)
            and HASH.fullmatch(reference) is not None,
            "invalid_evidence_ref",
        )
    return row | {"rating": float(rating) if rating is not None else None}


def load_records(data: bytes) -> list[dict]:
    require(0 < len(data) <= MAX_BYTES, "input_byte_limit")
    lines = data.splitlines()
    require(0 < len(lines) <= MAX_ROWS, "input_row_limit")
    rows = [validate_record(parse_json(line)) for line in lines]
    require(len({r["record_id"] for r in rows}) == len(rows), "duplicate_record_id")
    require(sum(len(r["text"]) for r in rows) <= 250_000, "aggregate_text_limit")
    return sorted(rows, key=lambda r: r["record_id"])


def normalized(text: str) -> str:
    return " ".join(WORDS.findall(unicodedata.normalize("NFKC", text).casefold()))


def components(rows: list[dict]) -> tuple[list[list[int]], dict[str, int]]:
    """Union product groups and exact/near text edges before any partition assignment."""
    parent = list(range(len(rows)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def join(i, j):
        first, second = root(i), root(j)
        if first != second:
            parent[max(first, second)] = min(first, second)

    products = {}
    texts = [normalized(r["text"]) for r in rows]
    shingles = []
    for i, row in enumerate(rows):
        group = row["product_group"]
        if group is not None:
            if group in products:
                join(products[group], i)
            else:
                products[group] = i
        words = texts[i].split()
        shingles.append(set(zip(words, words[1:], words[2:])))
    exact, near = 0, 0
    # ponytail: <=500 offline rows, bounded all-pairs; large corpora need a reviewed global index.
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if texts[i] == texts[j]:
                join(i, j)
                exact += 1
            elif shingles[i] and shingles[j]:
                overlap = len(shingles[i] & shingles[j])
                union = len(shingles[i]) + len(shingles[j]) - overlap
                if overlap * 5 >= union * 4:  # Jaccard >=0.80, no float boundary.
                    join(i, j)
                    near += 1
    groups = {}
    for i in range(len(rows)):
        groups.setdefault(root(i), []).append(i)
    return list(groups.values()), {"exact_pairs": exact, "near_pairs": near}


def audit(data: bytes, source: dict, seed: int = SEED) -> dict:
    require(type(seed) is int and 0 <= seed <= 2**32 - 1, "invalid_seed")
    require(
        source.get("admission") == "synthetic_only"
        and source.get("source_id") == "synthetic-fixture-v1",
        "source_not_admitted",
    )
    rows = load_records(data)
    groups, duplicate_stats = components(rows)
    labels = {r["record_id"]: resolve_label(r["votes"], synthetic=True) for r in rows}
    assignments = []
    for members in groups:
        group_hash = digest(encoded([rows[i]["record_id"] for i in members]))
        bucket = int(digest(f"{VERSION}:{seed}:{group_hash}".encode()), 16) % 100
        split = "train" if bucket < 70 else "validation" if bucket < 85 else "test"
        for i in members:
            row = rows[i]
            assignments.append(
                {
                    "record_id": row["record_id"],
                    "group_sha256": group_hash,
                    "text_sha256": digest(normalized(row["text"]).encode()),
                    "partition": split,
                    "label": labels[row["record_id"]],
                }
            )
    assignments.sort(key=lambda r: r["record_id"])
    partitions = {}
    for split in ("train", "validation", "test"):
        selected = [r for r in assignments if r["partition"] == split]
        partitions[split] = {
            "rows": len(selected),
            "labels": dict(sorted(Counter(r["label"] for r in selected).items())),
            "membership_sha256": digest(encoded(selected)),
        }
    quality = {
        "missing_rating": sum(r["rating"] is None for r in rows),
        "missing_timestamp": sum(r["timestamp"] is None for r in rows),
        "missing_product_group": sum(r["product_group"] is None for r in rows),
        "unsupported_category": sum(r["category"] != "electronics" for r in rows),
        "unsupported_language": sum(r["language"] != "en" for r in rows),
        "short_text_rows": sum(len(WORDS.findall(normalized(r["text"]))) < 5 for r in rows),
        "unknown_labels": sum(label == "unknown" for label in labels.values()),
        "conflicting_vote_rows": sum(
            len({v["decision"] for v in r["votes"] if v["decision"] != "unknown"}) > 1 for r in rows
        ),
        "missing_evidence_votes": sum(v["evidence_ref"] is None for r in rows for v in r["votes"]),
    }
    blocked = []
    if any(
        quality[k]
        for k in ("missing_product_group", "unsupported_category", "unsupported_language")
    ):
        blocked.append("incomplete_scope_or_product_groups")
    if any(p["rows"] == 0 for p in partitions.values()):
        blocked.append("empty_partition")
    if any(set(p["labels"]) != {"deceptive", "non_deceptive"} for p in partitions.values()):
        blocked.append("incomplete_binary_support")
    dated = [r["timestamp"] for r in rows if r["timestamp"] is not None]
    report = {
        "pipeline_version": VERSION,
        "source_id": source["source_id"],
        "source_card_sha256": digest(encoded(source)),
        "artifact_sha256": digest(data),
        "seed": seed,
        "target": "synthetic_scenario_only",
        "training_authorized": False,
        "training_reason": "no_approved_electronics_deception_dataset",
        "rows": len(rows),
        "text_lengths": {
            "min": min(len(r["text"]) for r in rows),
            "max": max(len(r["text"]) for r in rows),
            "total": sum(len(r["text"]) for r in rows),
        },
        "quality": quality,
        "label_counts": dict(sorted(Counter(labels.values()).items())),
        "label_basis_counts": dict(
            sorted(Counter(v["basis"] for r in rows for v in r["votes"]).items())
        ),
        "timestamp_range": {
            "earliest": min(dated) if dated else None,
            "latest": max(dated) if dated else None,
        },
        "groups": len(groups),
        "largest_group": max(map(len, groups)),
        "duplicates": duplicate_stats,
        "partition_policy": "group_hash_70_15_15_no_rebalance",
        "partition_diagnostics": blocked,
        "partitions": partitions,
        "assignments": assignments,
    }
    report["manifest_sha256"] = digest(encoded(report))
    return report


def read_bounded(path: Path) -> bytes:
    with path.open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "input_byte_limit")
    return data


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    args = parser.parse_args(argv)
    try:
        catalog = parse_json((ROOT / "sources.json").read_bytes())
        source = next((s for s in catalog["sources"] if s["source_id"] == args.source), None)
        require(source is not None, "unknown_source")
        # Permission gate runs before opening any supplied record file.
        require(source["admission"] == "synthetic_only", "source_not_admitted")
        report = audit(read_bounded(args.records), source, args.seed)
        if args.verify:
            previous = parse_json(read_bounded(args.verify))
            require(previous == report, "manifest_mismatch")
            print("audit_verified")
        else:
            target = args.output.resolve()
            require(
                target.is_relative_to((ROOT / "artifacts").resolve()), "output_outside_artifacts"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            # Freeze existing outputs: never overwrite a prior test membership manifest.
            with target.open("xb") as handle:
                handle.write(encoded(report) + b"\n")
            print("audit_written training_authorized=false")
        return 0
    except AuditError as error:
        print(str(error), file=sys.stderr)
    except (OSError, KeyError, TypeError, OverflowError):
        print("audit_io_or_schema_error", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
