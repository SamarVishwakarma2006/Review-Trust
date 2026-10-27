export type AnalysisResult = {
  schema_version: "1"; methodology_version: string; experimental: true;
  scope: "submitted_subset"; origin: "paste" | "csv"; review_count: number;
  score: { status: "experimental" | "insufficient_evidence"; value: number | null; reason_codes: string[] };
  confidence: { status: "not_validated"; level: null; explanation: string };
  coverage: { fields: Record<string, { present: number; missing: number }>; redactions: Record<string, number> };
  findings: { signal_id: string; assessment: "observed" | "not_observed" | "unavailable";
    explanation: string; coverage: { eligible: number; evaluated: number; total: number }; availability_reason: string | null;
    matching_review_count: number; references_truncated: boolean; supporting_review_refs: string[];
    evidence: { review_refs: string[]; matches: { phrase: string; start: number; end: number }[] }[] }[];
  reviews: { ref: string; text: string; title: string | null }[];
  warnings: { code: string; column_positions: number[] }[];
  limitations: string[];
};

const object = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);
const strings = (x: unknown): x is string[] => Array.isArray(x) && x.every(v => typeof v === "string");
const count = (x: unknown): x is number => Number.isSafeInteger(x) && (x as number) >= 0;

// Validate consumed fields before rendering; unknown fields are not displayed.
export function isResult(x: unknown): x is AnalysisResult {
  if (!object(x) || x.schema_version !== "1" || typeof x.methodology_version !== "string" || x.experimental !== true ||
    x.scope !== "submitted_subset" || !["paste", "csv"].includes(String(x.origin)) || !count(x.review_count) || x.review_count < 1 || x.review_count > 500) return false;
  const s = x.score, c = x.confidence, coverage = x.coverage;
  if (!object(s) || !strings(s.reason_codes) || !(s.status === "insufficient_evidence" && s.value === null ||
    s.status === "experimental" && count(s.value) && s.value <= 100) ||
    !object(c) || c.status !== "not_validated" || c.level !== null || typeof c.explanation !== "string" ||
    !object(coverage) || !object(coverage.fields) || !object(coverage.redactions) ||
    !Object.values(coverage.fields).every(v => object(v) && count(v.present) && count(v.missing)) ||
    !Object.values(coverage.redactions).every(count) || !strings(x.limitations)) return false;
  if (!Array.isArray(x.reviews) || x.reviews.length !== x.review_count || !x.reviews.every(r => object(r) &&
    typeof r.ref === "string" && /^r[1-9]\d*$/.test(r.ref) && typeof r.text === "string" && (r.title === null || typeof r.title === "string"))) return false;
  const refs = new Set(x.reviews.map(r => r.ref));
  if (refs.size !== x.review_count) return false;
  const validRefs = (v: unknown) => strings(v) && v.every(ref => refs.has(ref));
  return Array.isArray(x.findings) && x.findings.length <= 20 && x.findings.every(f => object(f) &&
    typeof f.signal_id === "string" && ["observed", "not_observed", "unavailable"].includes(String(f.assessment)) &&
    typeof f.explanation === "string" && (f.availability_reason === null || typeof f.availability_reason === "string") &&
    count(f.matching_review_count) && typeof f.references_truncated === "boolean" && validRefs(f.supporting_review_refs) &&
    object(f.coverage) && count(f.coverage.eligible) && count(f.coverage.evaluated) && count(f.coverage.total) &&
    Array.isArray(f.evidence) && f.evidence.every(e => object(e) && validRefs(e.review_refs) && Array.isArray(e.matches) &&
      e.matches.every(m => object(m) && typeof m.phrase === "string" && count(m.start) && count(m.end)))) &&
    Array.isArray(x.warnings) && x.warnings.every(w => object(w) && typeof w.code === "string" && Array.isArray(w.column_positions) && w.column_positions.every(count));
}

export function apiBase(value = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"): string {
  const url = new URL(value);
  if (!["http:", "https:"].includes(url.protocol) || url.username || url.password || url.search || url.hash || url.pathname !== "/") {
    throw new Error("Configure NEXT_PUBLIC_API_URL as an HTTP(S) origin, then restart or rebuild the web app.");
  }
  return url.origin;
}

export async function analyze(body: string | FormData, signal: AbortSignal): Promise<AnalysisResult> {
  let response: Response;
  const base = apiBase();
  try {
    response = await fetch(`${base}/v1/analyze${typeof body === "string" ? "" : "/csv"}`, {
      method: "POST", body, signal, cache: "no-store", credentials: "omit", redirect: "error",
      headers: typeof body === "string" ? { "Content-Type": "application/json" } : undefined,
    });
  } catch {
    throw new Error("Could not reach the analysis API. Check that it is running and its URL and allowed browser origin are configured.");
  }
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const messages: Record<number, string> = { 400: "The request is malformed.", 403: "This browser origin is not allowed by the API.",
      413: "The request exceeds an API limit. Reduce the file, review count or text length.", 415: "Use a UTF-8 CSV or supported JSON request.",
      422: "Correct the review data and try again.", 429: "Too many requests. Please wait before trying again.",
      503: "The API is busy or the analysis timed out. Try again later." };
    let message = messages[response.status] || "The API could not complete the analysis. Try again later.";
    const retry = response.headers.get("Retry-After");
    if (response.status === 429 && retry && /^\d{1,6}$/.test(retry)) message += ` Retry after ${retry} seconds.`;
    if (object(data) && object(data.error)) {
      const error = data.error;
      if (Array.isArray(error.fields)) {
        for (const f of error.fields.slice(0, 20)) {
          if (object(f) && (f.row === null || count(f.row)) && typeof f.field === "string" && /^[a-z_]{1,40}$/.test(f.field) && typeof f.code === "string" && /^[a-z_]{1,60}$/.test(f.code)) {
            message += ` ${f.row === null ? "Request" : `Row ${f.row}`} / ${f.field}: ${f.code.replaceAll("_", " ")}.`;
          }
        }
      }
      if (count(error.total_errors) && error.total_errors > 20) message += ` ${error.total_errors} issues in total; first 20 shown.`;
      if (typeof error.request_id === "string" && /^[a-f0-9]{32}$/.test(error.request_id)) message += ` Request ID: ${error.request_id}.`;
    }
    throw new Error(message);
  }
  if (!isResult(data)) throw new Error("The API returned an unsupported result. No score is displayed; check that web and API versions match.");
  return data;
}
