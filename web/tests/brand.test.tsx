import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import BrandView from "../app/brand";
import { brandEvidence } from "../lib/brand";
import { isComparison, type Comparison } from "../lib/comparison";

const products: Comparison["products"] = [0, 1, 2].map(i => ({
  role: i === 0 ? "original" : "alternative",
  report: { evidence_origin: "authored_fixture", product_title: `Synthetic Headphones H${i}`, status: i === 2 ? "empty" : "complete", analyzed_reviews: i === 2 ? 0 : 2, feedback: null,
    analysis: i === 2 ? null : { reviews: [{ ref: "r1", text: "Shared wording" }, { ref: "r2", text: "Shared wording" }], findings: [] } },
  offers: { decisions: [], comparison_complete: false, lowest_total_refs: [] },
}));
it("keeps product-local references and separates repeated rows from independent evidence", () => {
  const evidence = brandEvidence(products);
  expect(evidence.reviewed).toBe(2);
  expect(evidence.shared).toEqual([[{ product: 0, ref: "r1" }, { product: 0, ref: "r2" }, { product: 1, ref: "r1" }, { product: 1, ref: "r2" }]]);
  expect(evidence.issues.every(i => i.products.length === 0)).toBe(true);
  render(<BrandView result={{ version: "rt-comparison-0.1.0", brand: "Example (authored brand)", products }} />);
  expect(screen.getByText(/2 of 3 selected product samples contain reviews/)).toBeTruthy();
  expect(screen.getByText(/Manufacturer: unknown/)).toBeTruthy();
  expect(screen.getByText("Shared wording group 1: 4 rows across 2 products")).toBeTruthy();
});
it("rejects undeclared brand identities and incomplete brand scope", () => {
  expect(isComparison({ version: "rt-comparison-0.1.0", evidence_origin: "authored_fixture", brand: "Some real company", products })).toBe(false);
  expect(isComparison({ version: "rt-comparison-0.1.0", evidence_origin: "authored_fixture", brand: "Example (authored brand)", products: [] })).toBe(false);
});
