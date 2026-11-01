import { isDemo, type DemoResult } from "./demo";

type Offer = { ref: string; status: "comparable" | "unavailable"; total: string | null; observed_at: string; reasons: string[] };
export type Comparison = { version: "rt-comparison-0.1.0"; products: { role: "original" | "alternative"; report: DemoResult; offers: { decisions: Offer[]; comparison_complete: boolean; lowest_total_refs: string[] } }[] };
export function isComparison(value: unknown): value is Comparison {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return v.version === "rt-comparison-0.1.0" && v.evidence_origin === "authored_fixture" && Array.isArray(v.products) && v.products.length >= 1 && v.products.length <= 3 && v.products.every((p, i) => {
    if (!p || p.role !== (i === 0 ? "original" : "alternative") || !isDemo(p.report)) return false;
    const o = p.offers;
    if (!o || o.version !== "rt-offers-0.1.0" || o.evidence_origin !== "authored_fixture" || !Array.isArray(o.decisions) || o.decisions.length > 2 || typeof o.comparison_complete !== "boolean" || !Array.isArray(o.lowest_total_refs)) return false;
    if (!o.decisions.every((d: Offer & { currency: string }, n: number) => d && d.ref === `o${n + 1}` && d.currency === "INR" && typeof d.observed_at === "string" && Number.isFinite(Date.parse(d.observed_at)) && Array.isArray(d.reasons) && d.reasons.length <= 10 && d.reasons.every(r => typeof r === "string" && r.length <= 100) && (d.status === "comparable" ? typeof d.total === "string" && /^\d{1,10}\.\d{2}$/.test(d.total) && d.reasons.length === 0 : d.status === "unavailable" && d.total === null && d.reasons.length > 0))) return false;
    const complete = o.decisions.length > 0 && o.decisions.every((d: Offer) => d.status === "comparable");
    const minimum = Math.min(...o.decisions.map((d: Offer) => Number(d.total)));
    const expected = complete ? o.decisions.filter((d: Offer) => Number(d.total) === minimum).map((d: Offer) => d.ref) : [];
    return o.comparison_complete === complete && JSON.stringify(o.lowest_total_refs) === JSON.stringify(expected);
  });
}
