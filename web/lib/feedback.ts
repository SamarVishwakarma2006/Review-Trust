export const states = ["positive", "negative", "mixed", "unassessed"] as const;
type State = typeof states[number];
type Evidence = { ref: string; spans: { start: number; end: number }[] };
export type Feedback = { version: string; analyzed_reviews: number; aspects: { aspect: string; mentioned: number; counts: Record<State, number>; evidence: Record<State, Evidence[]>; omitted: Record<State, number> }[] };
export type DisplayReview = { ref: string; text: string };
const object = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null;
const count = (v: unknown): v is number => Number.isInteger(v) && Number(v) >= 0 && Number(v) <= 500;
export function validFeedback(v: unknown, reviews: unknown, total: number): boolean {
  if (!Array.isArray(reviews) || reviews.length !== total || !reviews.every(r => object(r) && typeof r.ref === "string" && typeof r.text === "string" && Array.from(r.text).length <= 5000)) return false;
  const lengths = new Map(reviews.map(r => [r.ref, Array.from(r.text).length]));
  if (lengths.size !== total || !object(v) || v.version !== "rt-feedback-0.1.0" || v.analyzed_reviews !== total || !Array.isArray(v.aspects) || v.aspects.length !== 4) return false;
  return v.aspects.every((a, i) => {
    if (!object(a) || a.aspect !== ["battery", "comfort", "durability", "sound"][i] || !count(a.mentioned) || a.mentioned > total || !object(a.counts) || !object(a.evidence) || !object(a.omitted)) return false;
    const counts = a.counts, evidence = a.evidence, omitted = a.omitted;
    let sum = 0;
    const seen = new Set<string>();
    for (const state of states) {
      const n = counts[state], rows = evidence[state];
      if (!count(n) || !Array.isArray(rows) || rows.length !== Math.min(n, 3) || omitted[state] !== n - rows.length) return false;
      sum += n;
      for (const row of rows) {
        if (!object(row) || typeof row.ref !== "string" || seen.has(row.ref) || !lengths.has(row.ref) || !Array.isArray(row.spans) || row.spans.length < 1 || row.spans.length > 2) return false;
        seen.add(row.ref);
        if (!row.spans.every(s => object(s) && Number.isInteger(s.start) && Number.isInteger(s.end) && Number(s.start) >= 0 && Number(s.end) > Number(s.start) && Number(s.end) <= lengths.get(row.ref)!)) return false;
      }
    }
    return sum === a.mentioned;
  });
}
