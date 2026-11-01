import { expect, test } from "vitest";
import { validFeedback, states } from "../lib/feedback";

test("feedback validates counts, references and Unicode spans before rendering", () => {
  const reviews = [{ ref: "r1", text: "😀. Battery included." }];
  const aspects = ["battery", "comfort", "durability", "sound"].map((aspect, i) => ({
    aspect, mentioned: i === 0 ? 1 : 0,
    counts: Object.fromEntries(states.map(s => [s, i === 0 && s === "unassessed" ? 1 : 0])),
    omitted: Object.fromEntries(states.map(s => [s, 0])),
    evidence: Object.fromEntries(states.map(s => [s, i === 0 && s === "unassessed" ? [{ ref: "r1", spans: [{ start: 3, end: 10 }] }] : []])),
  }));
  const report = { version: "rt-feedback-0.1.0", analyzed_reviews: 1, aspects };
  expect(validFeedback(report, reviews, 1)).toBe(true);
  aspects[0].counts.positive = 1;
  expect(validFeedback(report, reviews, 1)).toBe(false);
  aspects[0].counts.positive = 0;
  aspects[0].evidence.unassessed[0].spans[0].end = 100;
  expect(validFeedback(report, reviews, 1)).toBe(false);
  aspects[0].evidence.unassessed[0].spans[0].end = 10;
  aspects[0].evidence.unassessed[0].ref = "missing";
  expect(validFeedback(report, reviews, 1)).toBe(false);
});
