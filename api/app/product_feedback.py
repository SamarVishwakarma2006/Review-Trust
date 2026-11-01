"""Offline aspect wording counts over already validated, masked display reviews."""

import re

from app.analysis import check_deadline
from app.ingestion import ReviewInputError
from app.results import DisplayReview

VERSION = "rt-feedback-0.1.0"
ASPECTS = {
    "battery": (r"battery|batteries", r"(?:the\s+)?battery\s+is\s+(good|bad)"),
    "comfort": (
        r"comfort|comfortable|uncomfortable",
        r"these\s+(?:headphones|earphones)\s+are\s+(comfortable|uncomfortable)",
    ),
    "durability": (
        r"durability|durable|broke|broken",
        r"these\s+(?:headphones|earphones)\s+are\s+(durable|broken)",
    ),
    "sound": (r"sound|audio", r"(?:the\s+)?(?:sound|audio)\s+is\s+(good|bad)"),
}
ABSTAIN = re.compile(
    r"[\"'‘’“”]|\b(?:no|not|never|if|but|although|however|wish|sarcasm)\b|n't", re.I
)
STATES = ("positive", "negative", "mixed", "unassessed")


def summarize_feedback(reviews: tuple[DisplayReview, ...], deadline: float) -> dict:
    """No ingestion or masking here: callers must supply pipeline display records.

    Spans index the supplied display text, never casefolded/rewritten text.
    Return references only, so review bodies are not duplicated in output.
    """
    check_deadline(deadline)
    if (
        len(reviews) > 500
        or any(len(row.text) > 5000 for row in reviews)
        or sum(len(row.text) for row in reviews) > 250000
        or len({row.ref for row in reviews}) != len(reviews)
    ):
        raise ReviewInputError("feedback_input", "Invalid feedback sample.")
    aspects = []
    for aspect, (terms, phrase) in ASPECTS.items():
        counts = dict.fromkeys(STATES, 0)
        evidence = {state: [] for state in STATES}
        for row in reviews:
            check_deadline(deadline)
            mention = re.search(r"\b(?:" + terms + r")\b", row.text, re.I)
            if not mention:
                continue
            matches = {}
            if not ABSTAIN.search(row.text):
                for clause in re.finditer(r"[^.!?\n]+", row.text):
                    matched = re.fullmatch(r"\s*" + phrase + r"\s*", clause[0], re.I)
                    if matched:
                        state = (
                            "positive"
                            if matched[1].lower() in ("good", "comfortable", "durable")
                            else "negative"
                        )
                        start = clause.start() + len(clause[0]) - len(clause[0].lstrip())
                        end = clause.end() - len(clause[0]) + len(clause[0].rstrip())
                        matches.setdefault(state, {"start": start, "end": end})
            state = "mixed" if len(matches) == 2 else next(iter(matches), "unassessed")
            counts[state] += 1
            if len(evidence[state]) < 3:
                evidence[state].append(
                    {
                        "ref": row.ref,
                        "spans": list(matches.values())
                        or [{"start": mention.start(), "end": mention.end()}],
                    }
                )
        aspects.append(
            dict(
                aspect=aspect,
                mentioned=sum(counts.values()),
                counts=counts,
                evidence=evidence,
                omitted={state: counts[state] - len(evidence[state]) for state in STATES},
            )
        )
    check_deadline(deadline)
    return dict(version=VERSION, analyzed_reviews=len(reviews), aspects=aspects)
