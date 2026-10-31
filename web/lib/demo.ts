export type DemoResult = { evidence_origin: "authored_fixture"; status: "complete" | "partial" | "empty"; product_title: string; analyzed_reviews: number; analysis: null | { findings: { signal_id: string; explanation: string; assessment: string }[] } };
const object = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null;
export function isDemo(v: unknown): v is DemoResult {
  if (!object(v) || v.schema_version !== "2" || v.evidence_origin !== "authored_fixture" || v.ingestion_version !== "rt-fixture-analysis-0.1.0" || !["complete", "partial", "empty"].includes(String(v.status)) || typeof v.product_title !== "string" || v.product_title.length > 300 || !Number.isInteger(v.analyzed_reviews) || Number(v.analyzed_reviews) < 0 || Number(v.analyzed_reviews) > 500) return false;
  if (v.analysis === null) return v.analyzed_reviews === 0;
  const a = v.analysis;
  return object(a) && a.schema_version === "2" && a.origin === "authored_fixture" && a.review_count === v.analyzed_reviews && object(a.score) && a.score.value === null && ["withheld", "insufficient_evidence"].includes(String(a.score.status)) && Array.isArray(a.score.reason_codes) && a.score.reason_codes.includes("public_score_not_validated") && object(a.confidence) && a.confidence.level === null && a.confidence.status === "not_validated" && Array.isArray(a.findings) && a.findings.length <= 10 && a.findings.every(f => object(f) && typeof f.signal_id === "string" && typeof f.explanation === "string" && ["observed", "not_observed", "unavailable"].includes(String(f.assessment)));
}
