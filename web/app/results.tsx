import type { AnalysisResult } from "../lib/api";

const readable = (value: string) => value.replaceAll("_", " ");
export default function Results({ result }: { result: AnalysisResult }) {
  const reviews = new Map(result.reviews.map(r => [r.ref, r]));
  return <section className="panel" aria-labelledby="results-title">
    <p className="eyebrow">Experimental · Submitted subset only</p>
    <h2 id="results-title">Analysis results</h2>
    <p>{result.review_count} {result.review_count === 1 ? "review" : "reviews"} · {result.origin === "csv" ? "CSV upload" : "Pasted entries"}</p>
    <div className="score">
      <h3>Experimental Trust Score</h3>
      <p className="score-value">{result.score.value === null ? "Insufficient evidence" : `${result.score.value} / 100`}</p>
      <p>A higher value means fewer included patterns were observed. Even 100 does not verify authenticity. Missing evidence is not low risk.</p>
      {result.score.reason_codes.length > 0 && <ul>{result.score.reason_codes.map(reason => <li key={reason}>{readable(reason)}</li>)}</ul>}
      <p><strong>Confidence: not validated.</strong> {result.confidence.explanation}</p>
    </div>
    <h3>Evidence coverage</h3>
    <ul>{Object.entries(result.coverage.fields).map(([field, value]) => <li key={field}>{readable(field)}: {value.present} / {result.review_count} present; {value.missing} missing</li>)}</ul>
    <p>Common-pattern masking: {Object.entries(result.coverage.redactions).map(([kind, n]) => `${n} ${kind}`).join(", ")}. Other personal details may remain.</p>
    <h3>Findings</h3>
    {result.findings.map((f, i) => <article className="finding" key={i}>
      <h4>{readable(f.signal_id)} — {readable(f.assessment)}</h4>
      {!["text_repetition", "incentive_language"].includes(f.signal_id) && <p className="muted">Context only — does not affect the score.</p>}
      <p>{f.explanation}</p>
      {f.value && "histogram" in f.value && <>
        <p>Mean rating: {f.value.mean.toFixed(2)} / 5. Ratings ≤2: {(f.value.low_share * 100).toFixed(1)}%; ratings ≥4: {(f.value.high_share * 100).toFixed(1)}%.</p>
        <ul aria-label="Rating histogram">{f.value.histogram.map(bin => <li key={bin.rating}>{bin.rating} {bin.rating === 1 ? "star" : "stars"}: {bin.count} / {f.value && "rated_reviews" in f.value ? f.value.rated_reviews : 0} rated reviews</li>)}</ul>
      </>}
      {f.value && "window_start" in f.value && <p>UTC window: {f.value.window_start} through {f.value.window_end}. Observed date span: {f.value.observed_span_days} days.</p>}
      {f.value && "matching_reviews" in f.value && <p>{f.value.matching_reviews} / {f.value.eligible_reviews} eligible reviews in this pattern.</p>}
      <p>{f.coverage.eligible} / {f.coverage.total} eligible; {f.coverage.evaluated} / {f.coverage.total} evaluated.</p>
      {f.availability_reason && <p>Unavailable reason: {readable(f.availability_reason)}.</p>}
      {f.references_truncated && <p>Evidence preview is limited; {f.matching_review_count} matching reviews in total.</p>}
      {f.evidence.length > 0 && <details><summary>Inspect supporting reviews ({f.supporting_review_refs.length} references)</summary>
        {f.evidence.map((e, n) => <div key={n} className="evidence">
          {e.match_kind && <p>Pair method: {e.match_kind === "exact" ? "exact normalized text" : "word TF-IDF cosine"}{e.similarity != null ? `; similarity ${e.similarity.toFixed(4)}` : ""}. Similarity is not an authenticity probability.</p>}
          {e.rating != null && <p>Submitted rating: {e.rating} / 5{e.polarity ? `; lexicon direction: ${e.polarity}` : ""}.</p>}
          {e.timestamp_day && <p>Submitted date (UTC): {e.timestamp_day}</p>}
          <p>Evidence references: {e.review_refs.join(" + ")}</p>
          {e.review_refs.map(ref => { const review = reviews.get(ref)!; return <blockquote key={ref}><strong>{ref}</strong>{review.title && <p>{review.title}</p>}<p className="review-text">{review.text}</p></blockquote>; })}
          {e.matches.map((match, j) => <p key={j}>Matched word or phrase: “{match.phrase}” (characters {match.start}–{match.end}, zero-based Unicode offsets).</p>)}
        </div>)}
      </details>}
    </article>)}
    <h3>Scope and limitations</h3>
    <ul>{result.warnings.map((warning, i) => <li key={i}>{readable(warning.code)}{warning.column_positions.length > 0 ? `: column positions ${warning.column_positions.join(", ")}` : ""}</li>)}</ul>
    <ul>{result.limitations.map((limitation, i) => <li key={i}>{limitation}</li>)}</ul>
    <p className="muted">Methodology: {result.methodology_version}. Numeric scoring remains subject to evaluation and release review.</p>
  </section>;
}
