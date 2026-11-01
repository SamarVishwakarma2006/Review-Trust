import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import Demo from "../app/demo";
import { isComparison } from "../lib/comparison";

const fixture = () => ({ version: "rt-comparison-0.1.0", evidence_origin: "authored_fixture", products: [{ role: "original", report: { schema_version: "2", ingestion_version: "rt-fixture-analysis-0.1.0", evidence_origin: "authored_fixture", status: "empty", product_title: "Synthetic original", analyzed_reviews: 0, analysis: null, feedback: null }, offers: { version: "rt-offers-0.1.0", evidence_origin: "authored_fixture", comparison_complete: false, lowest_total_refs: [], decisions: [{ ref: "o1", currency: "INR", status: "unavailable", total: null, observed_at: "2026-11-01T00:00:00Z", reasons: ["incomplete_total"] }] } }] });
afterEach(() => vi.unstubAllGlobals());
it("rejects forged provenance, totals and favorable missing evidence", () => {
  expect(isComparison(fixture())).toBe(true);
  const v = fixture(); v.evidence_origin = "collected";
  expect(isComparison(v)).toBe(false);
  const incomplete = fixture(); incomplete.products[0].offers.comparison_complete = true;
  expect(isComparison(incomplete)).toBe(false);
  const badDate = fixture(); badDate.products[0].offers.decisions[0].observed_at = "unknown";
  expect(isComparison(badDate)).toBe(false);
});
it("renders missing evidence and no alternatives, then resets", async () => {
  const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => fixture() });
  vi.stubGlobal("fetch", fetcher);
  render(<Demo />);
  fireEvent.change(screen.getByLabelText("Choose an authored example"), { target: { value: "compare_empty" } });
  fireEvent.click(screen.getByText("Analyze synthetic example"));
  await waitFor(() => expect(screen.getByText("No eligible alternatives in this authored catalog.")).toBeTruthy());
  expect(screen.getByText("No review evidence available.")).toBeTruthy();
  expect(screen.getByText("Offer comparison incomplete; no lowest-price recommendation.")).toBeTruthy();
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({ example: "compare_empty" });
  fireEvent.click(screen.getByText("Reset demo"));
  expect(screen.queryByText("Synthetic original")).toBeNull();
});
