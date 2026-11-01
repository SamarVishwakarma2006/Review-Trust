import time

import pytest

from app.ingestion import ReviewInputError
from app.product_feedback import summarize_feedback
from app.results import DisplayReview


@pytest.mark.parametrize(
    "text,state",
    [
        ("The battery is good.", "positive"),
        ("The battery is bad.", "negative"),
        ("Battery included.", "unassessed"),
        ("The battery is not good.", "unassessed"),
        ("If the battery is good, I will buy it.", "unassessed"),
        ('"The battery is good."', "unassessed"),
        ("The battery is good. The battery is bad.", "mixed"),
        ("The battery is good. The battery is good.", "positive"),
        ("Batterylife is good.", None),
    ],
)
def test_authored_attribution(text, state):
    result = summarize_feedback((DisplayReview(ref="r1", text=text),), time.monotonic() + 5)
    battery = result["aspects"][0]
    assert battery["mentioned"] == (state is not None)
    assert battery["counts"] == {
        key: int(key == state) for key in ("positive", "negative", "mixed", "unassessed")
    }


def test_counts_spans_caps_and_deadline():
    text = "😀. Sound is good. These headphones are comfortable. These earphones are broken."
    reviews = tuple(DisplayReview(ref=f"r{i}", text=text) for i in range(5))
    result = summarize_feedback(reviews, time.monotonic() + 5)
    for aspect, state in zip(result["aspects"][1:], ("positive", "negative", "positive")):
        assert aspect["mentioned"] == aspect["counts"][state] == 5
        assert aspect["omitted"][state] == 2
        for evidence in aspect["evidence"][state]:
            for span in evidence["spans"]:
                assert text[span["start"] : span["end"]] in (
                    "Sound is good",
                    "These headphones are comfortable",
                    "These earphones are broken",
                )
    assert summarize_feedback((), time.monotonic() + 5)["analyzed_reviews"] == 0
    with pytest.raises(ReviewInputError):
        summarize_feedback(reviews, 0)
