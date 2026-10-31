import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import Home from "../app/page";
import { analyze, apiBase, isResult, type AnalysisResult } from "../lib/api";
import { csvHeaders, pasteBody } from "../lib/input";

const result: AnalysisResult = {
  schema_version: "1", methodology_version: "rt-patterns-0.3.0-experimental", experimental: true,
  scope: "submitted_subset", origin: "paste", review_count: 1,
  score: { status: "insufficient_evidence", value: null, reason_codes: ["public_score_not_validated", "too_few_reviews"] },
  confidence: { status: "not_validated", level: null, explanation: "Inspect evidence coverage instead." },
  coverage: { fields: { text: { present: 1, missing: 0 } }, redactions: { email: 0, phone: 0 } },
  findings: [{ value: { matching_reviews: 1, eligible_reviews: 1, fraction: 1 }, signal_id: "incentive_language", assessment: "observed", explanation: "A phrase mention was observed.",
    coverage: { eligible: 1, evaluated: 1, total: 1 }, availability_reason: null, matching_review_count: 1,
    references_truncated: false, supporting_review_refs: ["r1"], evidence: [{ review_refs: ["r1"], matches: [] }] }],
  reviews: [{ ref: "r1", text: '<script>alert("synthetic")</script>', title: null }],
  warnings: [{ code: "unverified_subset", column_positions: [] }], limitations: ["Selected subsets may be unrepresentative."],
};
const response = (data: unknown = result, status = 200, headers = {}) => new Response(JSON.stringify(data), { status, headers });
const confirm = () => fireEvent.click(screen.getByRole("checkbox"));
const submit = () => fireEvent.click(screen.getByRole("button", { name: "Analyze reviews" }));
function fill() { fireEvent.change(screen.getByLabelText("Review 1"), { target: { value: "This synthetic display is bright and clear." } }); confirm(); }
afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks(); vi.useRealTimers(); });

test("requires declaration, keeps duplicate editable entries and sends canonical JSON without credentials", async () => {
  const fetcher = vi.fn().mockResolvedValue(response()); vi.stubGlobal("fetch", fetcher);
  render(<Home />);
  expect(within(screen.getByRole("region", { name: "Analyze a review subset" })).getByText(/Remove names/)).toBeTruthy();
  submit(); expect(await screen.findByRole("alert")).toBeTruthy(); expect(fetcher).not.toHaveBeenCalled();
  fill(); fireEvent.click(screen.getByRole("button", { name: "Add review" }));
  fireEvent.change(screen.getByLabelText("Review 2"), { target: { value: "This synthetic display is bright and clear." } });
  submit(); await screen.findByRole("heading", { name: "Analysis results" });
  const [url, options] = fetcher.mock.calls[0];
  expect(url).toBe("http://127.0.0.1:8000/v1/analyze");
  expect(options).toMatchObject({ credentials: "omit", cache: "no-store", redirect: "error" });
  expect(JSON.parse(options.body)).toEqual({ schema_version: "1", category: "electronics", language: "en", origin: "paste", reviews: [
    { text: "This synthetic display is bright and clear." }, { text: "This synthetic display is bright and clear." }] });
  expect(screen.getByText("Insufficient evidence")).toBeTruthy();
  expect(screen.getByText("Confidence: not validated.")).toBeTruthy();
  expect(document.querySelector("script")).toBeNull();
  expect(screen.getByText('<script>alert("synthetic")</script>')).toBeTruthy();
  expect(document.activeElement?.getAttribute("tabindex")).toBe("-1");
  fireEvent.click(screen.getByRole("button", { name: "Reset input and results" }));
  expect(screen.queryByText("Analysis results")).toBeNull();
  expect((screen.getByLabelText("Review 1") as HTMLTextAreaElement).value).toBe("");
  expect((screen.getByRole("checkbox") as HTMLInputElement).checked).toBe(false);
});

test("cancel and reset abort active requests and ignore late completion", async () => {
  let resolve!: (value: Response) => void;
  const fetcher = vi.fn(() => new Promise<Response>(r => { resolve = r; })); vi.stubGlobal("fetch", fetcher);
  render(<Home />); fill(); submit();
  expect(within(screen.getByRole("region", { name: "Analyze a review subset" })).getByRole("status").textContent).toContain("Analyzing");
  fireEvent.click(screen.getByRole("button", { name: "Cancel analysis" }));
  expect((fetcher.mock.calls[0] as unknown as [string, RequestInit])[1].signal?.aborted).toBe(true);
  await act(async () => { resolve(response()); });
  expect(screen.queryByText("Analysis results")).toBeNull();
  submit(); fireEvent.click(screen.getByRole("button", { name: "Reset input and results" }));
  await act(async () => { resolve(response()); });
  expect(screen.queryByText("Analysis results")).toBeNull();
});

test("network failure retains input; retry succeeds with an experimental score", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValueOnce(new TypeError("private network details")).mockResolvedValueOnce(response({ ...result, score: { status: "withheld", value: null, reason_codes: ["public_score_not_validated"] } })));
  render(<Home />); fill(); submit();
  expect((await screen.findByRole("alert")).textContent).toContain("Could not reach");
  expect(screen.queryByText(/private network details/)).toBeNull();
  expect((screen.getByLabelText("Review 1") as HTMLTextAreaElement).value).toContain("synthetic");
  submit(); await screen.findByText("Score withheld");
  expect(screen.getByText(/Numeric scores are withheld/)).toBeTruthy();
});

test("CSV preview maps explicit columns and sends file plus metadata with fixed filename", async () => {
  const fetcher = vi.fn().mockResolvedValue(response({ ...result, origin: "csv" })); vi.stubGlobal("fetch", fetcher);
  render(<Home />); fireEvent.click(screen.getByRole("radio", { name: "Upload CSV" }));
  const file = new File(['Opinion,Stars,Name\n"A synthetic review",4,Ignored'], "private-name.csv", { type: "text/csv" });
  Object.defineProperty(file, "arrayBuffer", { value: async () => new TextEncoder().encode('Opinion,Stars,Name\n"A synthetic review",4,Ignored').buffer });
  fireEvent.change(screen.getByLabelText("UTF-8 CSV file"), { target: { files: [file] } });
  const opinion = await screen.findByLabelText("Column 1: Opinion");
  fireEvent.change(opinion, { target: { value: "text" } });
  fireEvent.change(screen.getByLabelText("Column 2: Stars"), { target: { value: "rating" } });
  confirm(); submit(); await screen.findByText("CSV upload", { exact: false });
  const [url, options] = fetcher.mock.calls[0]; const body = options.body as FormData;
  expect(url).toContain("/v1/analyze/csv"); expect(options.headers).toBeUndefined();
  expect(body.get("mapping")).toBe('{"Opinion":"text","Stars":"rating"}');
  expect(body.get("category")).toBe("electronics"); expect(body.get("language")).toBe("en"); expect(body.get("schema_version")).toBe("1");
  expect((body.get("file") as File).name).toBe("reviews.csv");
  fireEvent.click(screen.getByRole("button", { name: "Reset input and results" }));
  expect(screen.queryByLabelText("Column 1: Opinion")).toBeNull();
});

test("reset during CSV read discards the preview", async () => {
  let resolve!: (buffer: ArrayBuffer) => void;
  render(<Home />); fireEvent.click(screen.getByRole("radio", { name: "Upload CSV" }));
  const file = new File(["text\nsynthetic"], "reviews.csv");
  Object.defineProperty(file, "arrayBuffer", { value: () => new Promise<ArrayBuffer>(r => { resolve = r; }) });
  fireEvent.change(screen.getByLabelText("UTF-8 CSV file"), { target: { files: [file] } });
  fireEvent.click(screen.getByRole("button", { name: "Reset input and results" }));
  await act(async () => { resolve(new TextEncoder().encode("text\nsynthetic").buffer); });
  expect(screen.queryByText("Map columns")).toBeNull();
});

test("CSV header handles BOM, multiline and escaped quotes while rejecting ambiguity", () => {
  expect(csvHeaders('\uFEFF"Review, text","A""B","Multi\nline"\r\nignored')).toEqual(["Review, text", 'A"B', "Multi\nline"]);
  for (const invalid of ["text,text", "text,", 'ab"cd,rating', '"text"junk', '"unfinished', "x".repeat(101), Array.from({ length: 51 }, (_, i) => `c${i}`).join(",")]) expect(() => csvHeaders(invalid)).toThrow();
  expect(csvHeaders("text\nmalformed\"body")).toEqual(["text"]);
});

test("paste limits count Unicode code points and encoded bytes, preserving duplicates", () => {
  expect(JSON.parse(pasteBody(["😀".repeat(5000)])).reviews[0].text.length).toBe(10000);
  for (const entries of [[" "], ["x".repeat(5001)], Array(501).fill("x"), Array(51).fill("x".repeat(5000)), Array(50).fill("\u0001".repeat(5000))]) expect(() => pasteBody(entries)).toThrow();
});

test("API errors expose safe field locations and retry interval, never raw error message", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ error: { message: "PRIVATE BODY", fields: [{ row: 2, field: "rating", code: "out_of_range" }], total_errors: 1, request_id: "a".repeat(32) } }, 429, { "Retry-After": "6" })));
  await expect(analyze("{}", new AbortController().signal)).rejects.toThrow("Retry after 6 seconds. Row 2 / rating: out of range.");
});

test("unsupported responses fail closed; API URLs reject credentials and paths", async () => {
  expect(isResult(result)).toBe(true);
  expect(isResult({ ...result, score: { ...result.score, value: 0 } })).toBe(false);
  expect(isResult({ ...result, reviews: [] })).toBe(false);
  expect(isResult({ ...result, confidence: { level: "high" } })).toBe(false);
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ score: 100 })));
  await expect(analyze("{}", new AbortController().signal)).rejects.toThrow("unsupported result");
  for (const url of ["https://user:secret@example.com", "https://example.com/path", "file:///tmp/data", "https://example.com?secret=x"]) expect(() => apiBase(url)).toThrow();
  expect(apiBase("https://example.com/")).toBe("https://example.com");
});

test("HTTP size and timeout failures remain actionable", async () => {
  for (const [status, message] of [[413, "exceeds an API limit"], [503, "busy or the analysis timed out"]] as const) {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({}, status)));
    await expect(analyze("{}", new AbortController().signal)).rejects.toThrow(message);
  }
});

test("client deadline aborts a stalled request", async () => {
  vi.useFakeTimers();
  const fetcher = vi.fn(() => new Promise<Response>(() => {})); vi.stubGlobal("fetch", fetcher);
  render(<Home />); fill(); submit();
  await act(async () => { vi.advanceTimersByTime(35_000); });
  expect(screen.getByRole("alert").textContent).toContain("took too long");
  expect((fetcher.mock.calls[0] as unknown as [string, RequestInit])[1].signal?.aborted).toBe(true);
});

test("unmount aborts the active request", async () => {
  const fetcher = vi.fn(() => new Promise<Response>(() => {})); vi.stubGlobal("fetch", fetcher);
  const view = render(<Home />); fill(); submit(); view.unmount();
  await waitFor(() => expect((fetcher.mock.calls[0] as unknown as [string, RequestInit])[1].signal?.aborted).toBe(true));
});

test("versioned contextual evidence displays histogram, dates, rating direction and pair similarity", async () => {
  const contextual: AnalysisResult = { ...result, findings: [
    { ...result.findings[0], signal_id: "text_repetition", evidence: [{ review_refs: ["r1"], matches: [], match_kind: "tfidf", similarity: 0.95 }] },
    { ...result.findings[0], signal_id: "rating_distribution", value: { rated_reviews: 20, histogram: [{ rating: 4.5, count: 20 }], mean: 4.5, low_share: 0, high_share: 1 } },
    { ...result.findings[0], signal_id: "review_burst", value: { matching_reviews: 10, eligible_reviews: 20, fraction: 0.5, window_start: "2020-01-01", window_end: "2020-01-03", observed_span_days: 28 }, evidence: [{ review_refs: ["r1"], matches: [], timestamp_day: "2020-01-02" }] },
    { ...result.findings[0], signal_id: "rating_text_disagreement", evidence: [{ review_refs: ["r1"], matches: [], rating: 1, polarity: "positive" }] },
  ] };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response(contextual)));
  render(<Home />); fill(); submit(); await screen.findByText(/4.5 stars: 20/);
  expect(screen.getAllByText("Context only — does not affect the score.")).toHaveLength(3);
  expect(screen.getByText(/Submitted date \(UTC\): 2020-01-02/)).toBeTruthy();
  expect(screen.getByText(/lexicon direction: positive/)).toBeTruthy();
  expect(screen.getByText(/similarity 0.9500/)).toBeTruthy();
  expect(isResult({ ...result, methodology_version: "rt-patterns-0.1.0-experimental" })).toBe(false);
  expect(isResult({ ...contextual, findings: [{ ...contextual.findings[1], value: { histogram: "invalid" } }] })).toBe(false);
});
