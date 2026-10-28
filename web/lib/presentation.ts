import type { AnalysisResult } from "./api";

export type Finding = AnalysisResult["findings"][number];
export const readable = (value: string) => value.replaceAll("_", " ");
export const labels: Record<string, string> = {
  text_repetition: "Text repetition", incentive_language: "Incentive-language mentions",
  review_burst: "Review timing", rating_distribution: "Rating distribution",
  rating_text_disagreement: "Rating and wording",
};
export const withholding: Record<string, string> = {
  too_few_reviews: "At least 20 submitted reviews are needed for a score.",
  too_few_eligible_reviews: "At least 20 reviews need five remaining word tokens each.",
  low_text_coverage: "At least 80% of submitted reviews need eligible text.",
  scoring_signal_unavailable: "Both scoring methods must be available; inspect their evidence gaps below.",
};
export const scoring = (id: string) => id === "text_repetition" || id === "incentive_language";

export function priority(findings: Finding[]) {
  const states = { observed: 0, unavailable: 1, not_observed: 2 };
  return findings.map((finding, index) => ({ finding, index })).sort((a, b) =>
    states[a.finding.assessment] - states[b.finding.assessment] ||
    Number(scoring(b.finding.signal_id)) - Number(scoring(a.finding.signal_id)) || a.index - b.index,
  ).slice(0, 3);
}

// API offsets index Unicode code points, not JavaScript UTF-16 code units.
export function markedParts(text: string, matches: { start: number; end: number }[]) {
  const points = Array.from(text);
  const spans: { start: number; end: number }[] = [];
  for (const match of [...matches].sort((a, b) => a.start - b.start)) {
    if (!Number.isSafeInteger(match.start) || !Number.isSafeInteger(match.end) ||
      match.start < 0 || match.end <= match.start || match.end > points.length) continue;
    const previous = spans.at(-1);
    if (previous && match.start <= previous.end) previous.end = Math.max(previous.end, match.end);
    else spans.push({ ...match });
  }
  const parts: { text: string; marked: boolean }[] = [];
  let cursor = 0;
  for (const span of spans) {
    if (span.start > cursor) parts.push({ text: points.slice(cursor, span.start).join(""), marked: false });
    parts.push({ text: points.slice(span.start, span.end).join(""), marked: true });
    cursor = span.end;
  }
  if (cursor < points.length) parts.push({ text: points.slice(cursor).join(""), marked: false });
  return parts;
}
