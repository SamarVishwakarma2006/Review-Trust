import type { Comparison } from "../lib/comparison";
import { states } from "../lib/feedback";
import BrandView from "./brand";

export default function ComparisonView({ result }: { result: Comparison }) {
  return <section aria-label="Synthetic product comparison">
    {result.brand && <BrandView result={result} />}
    <h3>Compare authored alternatives</h3>
    <p>All products, reviews and offers here are synthetic. Eligibility: wireless over-ear headphones with a microphone. Original first, then catalog order; no ranking weights or quality winner. Prices do not determine the order.</p>
    <p>Specifications shared by these examples: black, new, India region, one pair of headphones. Offer context: demo_IN; unconditional INR totals include shipping, tax and mandatory fees when known. Observations must be within 24 hours of analysis. They are not live quotes.</p>
    <p>Numeric scores and confidence are withheld. Missing evidence is unknown, never a favorable result. Review counts differ and repeated reviews are not independent buyers.</p>
    {result.products.length === 1 && <p>No eligible alternatives in this authored catalog.</p>}
    <div className="comparison-grid">{result.products.map((p, i) => <article className="finding" key={i}>
      <h4>{p.report.product_title}</h4>
      <p>{p.role === "original" ? "Original product" : "Alternative: matches all four requested specifications."}</p>
      <p>{p.report.analyzed_reviews} sampled reviews · {p.report.status} sample. Real-world total unknown.</p>
      {p.report.status === "partial" && <p>Collection stopped early; this is an incomplete sample.</p>}
      <h5>Authored offers</h5>
      {p.offers.decisions.map(o => <p key={o.ref}>{o.ref}: {o.total === null ? `Total unknown (${o.reasons.join(", ").replaceAll("_", " ")})` : `INR ${o.total}`} · observed {o.observed_at}</p>)}
      <p>{p.offers.comparison_complete ? `Lowest supplied total for this product: ${p.offers.lowest_total_refs.join(", ")}${p.offers.lowest_total_refs.length > 1 ? " (tie)" : ""}.` : "Offer comparison incomplete; no lowest-price recommendation."}</p>
      <h5>Reported feedback</h5>
      {!p.report.feedback ? <p>No review evidence available.</p> : p.report.feedback.aspects.map(a => <details key={a.aspect}>
        <summary>{a.aspect}: mentioned in {a.mentioned} of {p.report.analyzed_reviews} reviews</summary>
        {states.map(s => <div key={s}><p>{s}: {a.counts[s]}</p>{a.evidence[s].map(e => <blockquote key={e.ref}>{e.spans.map((span, n) => <p key={n}>{e.ref}: {Array.from(p.report.analysis!.reviews.find(r => r.ref === e.ref)!.text).slice(span.start, span.end).join("")}</p>)}</blockquote>)}{a.omitted[s] > 0 && <p>{a.omitted[s]} additional examples omitted.</p>}</div>)}
      </details>)}
      <details><summary>Review-pattern findings</summary>{p.report.analysis?.findings.map(f => <p key={f.signal_id}>{f.assessment}: {f.explanation}</p>) ?? <p>No analysis available.</p>}</details>
    </article>)}</div>
  </section>;
}
