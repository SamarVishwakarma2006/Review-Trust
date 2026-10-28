"use client";

import { useState } from "react";
import type { AnalysisResult, RatingEvidence } from "../lib/api";
import { labels, markedParts, priority, readable, scoring, withholding } from "../lib/presentation";

function Bar({ count, total }: { count: number; total: number }) {
  return <span className="bar-track" aria-hidden="true"><span style={{ width: `${total > 0 ? Math.min(100, count / total * 100) : 0}%` }} /></span>;
}

function RatingChart({ value }: { value: RatingEvidence }) {
  return <figure className="chart">
    <figcaption>Rating histogram <span className="muted">· exact submitted values</span></figcaption>
    <p>Mean rating: {value.mean.toFixed(2)} / 5. Ratings ≤2: {(value.low_share * 100).toFixed(1)}%; ratings ≥4: {(value.high_share * 100).toFixed(1)}%.</p>
    <ul className="bar-list" aria-label="Rating histogram">{value.histogram.map(bin => <li key={bin.rating}>
      <span>{bin.rating} {bin.rating === 1 ? "star" : "stars"}: {bin.count} / {value.rated_reviews} rated reviews</span>
      <Bar count={bin.count} total={value.rated_reviews} />
    </li>)}</ul>
  </figure>;
}

export default function Results({ result }: { result: AnalysisResult }) {
  const [measure, setMeasure] = useState<"evaluated" | "eligible">("evaluated");
  const reviews = new Map(result.reviews.map(r => [r.ref, r]));
  const available = result.findings.filter(f => f.assessment !== "unavailable").length;
  const textCoverage = result.findings.find(f => f.signal_id === "text_repetition")?.coverage;
  return <section className="results" aria-labelledby="results-title">
    <div className="results-heading">
      <div><p className="eyebrow">Your submitted subset</p><h2 id="results-title">Analysis results</h2></div>
      <p className="result-source">{result.review_count} {result.review_count === 1 ? "review" : "reviews"} · {result.origin === "csv" ? "CSV upload" : "Pasted entries"}</p>
    </div>
    <div className="result-grid">
      <section className="score-card" aria-labelledby="score-title">
        <span className="badge">Experimental index</span>
        <h3 id="score-title">Experimental Trust Score</h3>
        <p className={`score-value ${result.score.value === null ? "withheld" : ""}`}>{result.score.value === null ? "Insufficient evidence" : `${result.score.value} / 100`}</p>
        <p>A higher value means fewer included patterns were observed. Even 100 does not verify authenticity. Missing evidence is not low risk.</p>
        {result.score.reason_codes.length > 0 && <ul className="score-reasons">{result.score.reason_codes.map(reason => <li key={reason}>{withholding[reason] || readable(reason)}</li>)}</ul>}
        <details className="method-note"><summary>How this index is calculated</summary>
          <p>Only repetition and incentive-mention shares contribute. The index is 100 × (1 − the larger share), rounded half-up. Evidence gates can withhold it. Contextual findings do not change it.</p>
          <p>Templates, duplicate ingestion, quotations and negations can explain the included patterns. Numerical values are not probabilities or purchasing advice.</p>
        </details>
      </section>
      <aside className="coverage-card" aria-label="Evidence at a glance">
        <p className="eyebrow">Read with the score</p>
        <dl className="coverage-stats">
          <div><dt>Submitted reviews</dt><dd>{result.review_count}</dd></div>
          <div><dt>Eligible text reviews</dt><dd>{textCoverage ? `${textCoverage.eligible} / ${textCoverage.total}` : "Not returned"}</dd></div>
          <div><dt>Available methods</dt><dd>{available} / {result.findings.length}</dd></div>
        </dl>
        <p><strong>Confidence: not validated.</strong> {result.confidence.explanation}</p>
        <p className="muted">No trained authenticity classifier or probability calibration is available. This subset may not represent all product reviews.</p>
      </aside>
    </div>

    <section className="panel" aria-labelledby="first-findings">
      <p className="eyebrow">Start here</p><h3 id="first-findings">Three findings to inspect</h3>
      <p className="muted">Observed patterns first, then evidence gaps, then unobserved methods. Within each state, scoring methods come first, then the order shown in the full findings. This order is not a severity rating.</p>
      <ol className="finding-shortlist" aria-label="Priority findings">{priority(result.findings).map(({ finding: f, index }) => <li key={index}>
        <a href={`#finding-${index}`}><span>{labels[f.signal_id] || readable(f.signal_id)}</span><span className={`state state-${f.assessment}`}>{readable(f.assessment)}</span></a>
        <p>{f.assessment === "unavailable" ? "Evidence unavailable; inspect the requirements." : `${f.matching_review_count} matching ${f.matching_review_count === 1 ? "review" : "reviews"}; ${f.coverage.evaluated} / ${f.coverage.total} evaluated.`}</p>
      </li>)}</ol>
    </section>

    <section className="panel" aria-labelledby="coverage-title">
      <h3 id="coverage-title">Evidence coverage</h3>
      <p>Coverage describes available data, not accuracy. Eligible rows have usable inputs for a method; sample and coverage gates may still prevent evaluation. Evaluated rows were actually assessed.</p>
      <fieldset className="chart-controls"><legend>Chart measure</legend>
        <label><input type="radio" name="coverage-measure" checked={measure === "evaluated"} onChange={() => setMeasure("evaluated")} /> Evaluated rows</label>
        <label><input type="radio" name="coverage-measure" checked={measure === "eligible"} onChange={() => setMeasure("eligible")} /> Eligible rows</label>
      </fieldset>
      <ul className="bar-list" aria-label="Signal coverage">{result.findings.map((f, index) => <li key={index}>
        <span>{labels[f.signal_id] || readable(f.signal_id)}: <strong>{f.coverage[measure]} / {f.coverage.total} {measure}</strong></span>
        <Bar count={f.coverage[measure]} total={f.coverage.total} />
        {f.assessment === "unavailable" && <small>Unavailable: {readable(f.availability_reason || "not returned")}</small>}
      </li>)}</ul>
      <details className="field-coverage"><summary>Inspect field presence and missing data</summary>
        <ul>{Object.entries(result.coverage.fields).map(([field, value]) => <li key={field}>{readable(field)}: {value.present} / {result.review_count} present; {value.missing} missing</li>)}</ul>
      </details>
      <p className="muted">Common-pattern masking: {Object.entries(result.coverage.redactions).map(([kind, n]) => `${n} ${kind}`).join(", ")}. Other personal details may remain.</p>
    </section>

    <section className="panel" aria-labelledby="findings-title">
      <h3 id="findings-title">All findings and supporting reviews</h3>
      <p className="muted">Inspect the returned evidence in context. Highlighted spans show matched wording; they do not establish conduct.</p>
      {result.findings.map((f, i) => <article className="finding" key={i}>
        <div className="finding-heading"><h4 id={`finding-${i}`} tabIndex={-1}>{labels[f.signal_id] || readable(f.signal_id)}</h4><span className={`state state-${f.assessment}`}>{readable(f.assessment)}</span></div>
        <p className="finding-role">{scoring(f.signal_id) ? "Included in the experimental score when available." : "Context only — does not affect the score."}</p>
        <p>{f.explanation}</p>
        {f.value && "histogram" in f.value && <RatingChart value={f.value} />}
        {f.value && "window_start" in f.value && <p className="value-note">UTC window: {f.value.window_start} through {f.value.window_end}. Observed date span: {f.value.observed_span_days} days.</p>}
        {f.value && "matching_reviews" in f.value && <p className="value-note">{f.value.matching_reviews} / {f.value.eligible_reviews} eligible reviews in this measured pattern.</p>}
        <p className="muted">{f.coverage.eligible} / {f.coverage.total} eligible; {f.coverage.evaluated} / {f.coverage.total} evaluated.</p>
        {f.availability_reason && <p className="gap-note">Unavailable reason: {readable(f.availability_reason)}.</p>}
        {f.references_truncated && <p>Evidence preview is limited; {f.matching_review_count} matching reviews in total.</p>}
        {f.evidence.length === 0 && <p className="muted">{f.assessment === "unavailable" ? "No supporting evidence is available for this method." : "No matching review evidence was returned."}</p>}
        {f.evidence.length > 0 && <details className="supporting"><summary>Inspect supporting reviews ({f.supporting_review_refs.length} {f.supporting_review_refs.length === 1 ? "reference" : "references"})</summary>
          {f.signal_id === "text_repetition" && <p className="muted">At most ten qualifying pairs are previewed. A similarity value describes text overlap, not authenticity.</p>}
          {f.evidence.map((e, n) => <div key={n} className="evidence">
            <p className="evidence-label">Evidence {n + 1} · {e.review_refs.join(" + ")}</p>
            {e.match_kind && <p>Pair method: {e.match_kind === "exact" ? "exact normalized text" : "word TF-IDF cosine"}{e.similarity != null ? `; similarity ${e.similarity.toFixed(4)}` : ""}. Similarity is not an authenticity probability.</p>}
            {e.rating != null && <p>Submitted rating: {e.rating} / 5{e.polarity ? `; lexicon direction: ${e.polarity}` : ""}.</p>}
            {e.timestamp_day && <p>Submitted date (UTC): {e.timestamp_day}</p>}
            {e.review_refs.map(ref => { const review = reviews.get(ref)!; return <blockquote key={ref}>
              <strong>{ref}</strong>{review.title && <p>{review.title}</p>}
              <p className="review-text">{markedParts(review.text, e.review_refs.length === 1 ? e.matches : []).map((part, index) => part.marked ? <mark key={index}>{part.text}</mark> : part.text)}</p>
            </blockquote>; })}
            {e.matches.map((match, j) => <p className="muted" key={j}>Matched word or phrase: “{match.phrase}” (characters {match.start}–{match.end}, zero-based Unicode offsets; end excluded).</p>)}
          </div>)}
        </details>}
      </article>)}
    </section>
    <section className="panel limitations" aria-labelledby="limits-title">
      <h3 id="limits-title">Scope and limitations</h3>
      <ul>{result.warnings.map((warning, i) => <li key={i}>{readable(warning.code)}{warning.column_positions.length > 0 ? `: column positions ${warning.column_positions.join(", ")}` : ""}</li>)}</ul>
      <ul>{result.limitations.map((limitation, i) => <li key={i}>{limitation}</li>)}</ul>
      <p className="muted">Methodology: {result.methodology_version}. Numeric scoring remains subject to evaluation and release review.</p>
    </section>
  </section>;
}
