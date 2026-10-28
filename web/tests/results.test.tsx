import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import Results from "../app/results";
import { isResult, type AnalysisResult } from "../lib/api";
import { markedParts, priority } from "../lib/presentation";
import fixture from "./fixtures/analysis.json";

const result = fixture as AnalysisResult;
afterEach(cleanup);

test("real API fixture remains compatible; three summary links follow disclosed priority", () => {
  expect(isResult(fixture)).toBe(true);
  render(<Results result={result} />);
  expect(screen.getByText("Score withheld")).toBeTruthy();
  const list = screen.getByRole("list", { name: "Priority findings" });
  // Scope via the ordered list so full-finding headings do not masquerade as summary links.
  expect(list.tagName).toBe("OL");
  const links = within(list).getAllByRole("link");
  expect(links.map(a => a.getAttribute("href"))).toEqual(["#finding-0", "#finding-1", "#finding-2"]);
  for (const link of links) expect(document.querySelector(link.getAttribute("href")!)?.getAttribute("tabindex")).toBe("-1");
  expect(screen.getByText(/This order is not a severity rating/)).toBeTruthy();
});

test("coverage control exposes evaluated versus eligible counts and explicit gaps", () => {
  const changed = structuredClone(result);
  changed.findings[0] = { ...changed.findings[0], assessment: "unavailable", value: null,
    availability_reason: "feature_limit", coverage: { eligible: 20, evaluated: 0, total: 20 }, evidence: [], supporting_review_refs: [], matching_review_count: 0 };
  render(<Results result={changed} />);
  const coverage = screen.getByRole("list", { name: "Signal coverage" });
  expect(within(coverage).getAllByText("0 / 20 evaluated")).toHaveLength(2);
  fireEvent.click(screen.getByRole("radio", { name: "Eligible rows" }));
  expect(within(coverage).getAllByText("20 / 20 eligible").length).toBeGreaterThan(0);
  expect(within(coverage).getByText(/Unavailable: feature limit/)).toBeTruthy();
  expect(screen.getByRole("radio", { name: "Eligible rows" }).getAttribute("type")).toBe("radio");
  expect(screen.getByText("Confidence: not validated.")).toBeTruthy();
});

test("rating bars have exact text counts; unavailable methods show no invented histogram", () => {
  render(<Results result={result} />);
  const histogram = screen.getByRole("list", { name: "Rating histogram" });
  expect(within(histogram).getByText("5 stars: 18 / 20 rated reviews")).toBeTruthy();
  expect(within(histogram).getByText("2 stars: 2 / 20 rated reviews")).toBeTruthy();
  expect(screen.getAllByText("Context only — does not affect the score.")).toHaveLength(3);
  expect(screen.getByText(/No supporting evidence is available/)).toBeTruthy();
  cleanup();
  const unavailable = { ...result, findings: result.findings.map(f => f.signal_id === "rating_distribution" ?
    { ...f, assessment: "unavailable" as const, value: null, availability_reason: "insufficient_rated_reviews", evidence: [] } : f) };
  render(<Results result={unavailable} />);
  expect(screen.queryByRole("list", { name: "Rating histogram" })).toBeNull();
});

test("supporting text and Unicode match spans render as escaped highlighted content", () => {
  const view = render(<Results result={result} />);
  const incentive = view.container.querySelectorAll(".finding")[1];
  fireEvent.click(within(incentive as HTMLElement).getByText(/Inspect supporting reviews/));
  const mark = incentive.querySelector("mark");
  expect(mark?.textContent?.toLowerCase()).toBe("received this product for free");
  expect(incentive.querySelector(".review-text")?.textContent?.startsWith("😀")).toBe(true);
  expect(view.container.querySelector("script")).toBeNull();
  expect(screen.getAllByText("<script>synthetic title</script>").length).toBeGreaterThan(0);
  const text = '😀 <img src=x> phrase text';
  const parts = markedParts(text, [{ start: 2, end: 13 }, { start: 5, end: 8 }]);
  expect(parts.map(p => p.text).join("")).toBe(text);
  expect(parts.filter(p => p.marked).map(p => p.text)).toEqual(["<img src=x>"]);
  expect(markedParts(text, [{ start: 999, end: 1000 }])).toEqual([{ text, marked: false }]);
});

test("numeric results are rejected and never rendered; unavailable reasons are actionable", () => {
  const forged = { ...result, score: { ...result.score, value: 0 } } as unknown as AnalysisResult;
  expect(isResult(forged)).toBe(false);
  render(<Results result={forged} />);
  expect(screen.getByText("Score withheld")).toBeTruthy();
  expect(screen.queryByText("0 / 100")).toBeNull();
  cleanup();
  render(<Results result={{ ...result, score: { ...result.score, value: null, status: "insufficient_evidence", reason_codes: ["low_text_coverage"] } }} />);
  expect(screen.getByText("Insufficient evidence")).toBeTruthy();
  expect(screen.queryByText("0 / 100")).toBeNull();
  expect(screen.getByText("At least 80% of submitted reviews need eligible text.")).toBeTruthy();
  expect(screen.getByText(/Numeric scores are withheld/)).toBeTruthy();
});

test("presentation priority preserves the source and treats gaps separately from absent observations", () => {
  const rows = result.findings.map(f => ({ ...f, assessment: "not_observed" as const }));
  const changed: AnalysisResult["findings"] = rows.map((f, i) => ({ ...f, assessment: i === 3 ? "observed" : i === 4 ? "unavailable" : f.assessment }));
  expect(priority(changed).map(f => f.index)).toEqual([3, 4, 0]);
  expect(changed.map(f => f.signal_id)).toEqual(rows.map(f => f.signal_id));
});

test("API boundary rejects reversed or out-of-range evidence offsets", () => {
  for (const match of [{ start: 10, end: 5 }, { start: 0, end: 100000 }]) {
    const invalid = structuredClone(fixture);
    invalid.findings[1].evidence[0].matches[0] = { ...invalid.findings[1].evidence[0].matches[0], ...match };
    expect(isResult(invalid)).toBe(false);
  }
});

