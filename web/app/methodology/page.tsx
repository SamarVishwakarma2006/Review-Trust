import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Methodology and limitations | ReviewTrust" };

export default function Methodology() {
  return (
    <main id="content" tabIndex={-1} className="content-page">
      <header><p className="eyebrow">Methodology · rt-patterns-0.3.0-experimental</p><h1>Evidence, with its limits.</h1><p className="intro">Deterministic pattern checks for the reviews you submit. No authenticity verdict.</p><p>Updated 28 October 2026. This method is experimental and unvalidated for deception detection.</p></header>
      <section className="panel" aria-labelledby="method-scope">
        <h2 id="method-scope">Scope and preprocessing</h2>
        <p>The analyzer assumes English reviews for one electronics product. These are your declarations, not detected or verified facts. Mixed languages, products and unrepresentative selections can invalidate interpretation.</p>
        <p>Common emails and phone numbers are masked before matching and returned text. Masking is incomplete. Unicode NFKC normalization, case folding and collapsed whitespace standardize text for matching; masked contact placeholders are excluded from comparison. Titles do not contribute to text signals.</p>
        <p>Text eligibility requires at least five remaining Unicode letter/digit word tokens. Short reviews remain in the submitted count. Signal coverage distinguishes eligible rows from rows actually evaluated.</p>
      </section>
      <section className="panel" aria-labelledby="method-text">
        <h2 id="method-text">Two text checks feed the offline research index</h2>
        <h3>Repetition</h3>
        <p>With at least ten eligible rows, count each eligible row that has another normalized exact match or TF-IDF cosine similarity of at least 0.90. TF-IDF uses word unigrams and adjacent bigrams, raw term counts, IDF = 1 + ln((1 + n) / (1 + document frequency)) and L2 normalization within this submission. There is no fitted global vocabulary or learned classifier.</p>
        <p>More than 20,000 vocabulary features makes repetition unavailable; it does not produce a partial numeric score. Supporting pairs are deterministic and bounded. Templates, shared descriptions, redaction collisions and duplicate ingestion can explain a match.</p>
        <h3>Incentive language</h3>
        <p>With at least ten eligible rows, count literal mentions of these four phrases, ignoring case and allowing whitespace variation:</p>
        <ul><li>in exchange for a review</li><li>received this product for free</li><li>received a free product</li><li>discount in exchange for</li></ul>
        <p>Quoted and negated phrases still count as mentions. Other wording can be missed. A mention does not establish an undisclosed incentive or a rule violation.</p>
      </section>
      <section className="panel" aria-labelledby="method-context">
        <h2 id="method-context">Three checks provide context only</h2>
        <dl className="method-list">
          <dt>Review timing</dt><dd>Requires at least 20 dated rows, 80% timestamp coverage and a 28-day observed span. Reports the busiest inclusive three-calendar-day UTC window; a share of at least 50% is observed. Launches, promotions and selection can explain concentration.</dd>
          <dt>Rating distribution</dt><dd>Requires at least 20 rated rows and 80% rating coverage. Shows exact rating bins and the mean; at least 90% at ratings ≤2 or ≥4 is observed concentration. Product quality can legitimately explain it.</dd>
          <dt>Rating/text disagreement</dt><dd>Requires at least 20 rated rows with supported, unambiguous English lexicon polarity. Reports low ratings (≤2) with positive wording or high ratings (≥4) with negative wording. Mixed, negated and unsupported text can abstain. Sarcasm and different product aspects can mislead this narrow lexicon.</dd>
        </dl>
        <p>None of these three checks changes the index. Missing metadata remains unavailable; it cannot silently improve a score.</p>
      </section>
      <section className="panel limitations" aria-labelledby="method-index">
        <h2 id="method-index">What the experimental index means</h2>
        <p>Let d be the fraction of eligible rows with repetition, and i the fraction with a listed incentive mention. The offline research index is 100 × (1 − max(d, i)), rounded to the nearest integer with exact halves rounded up. The two penalties are not added.</p>
        <p>It is withheld below 20 submitted rows, below 20 eligible rows, below 80% eligible text coverage, or when either text check is unavailable or the analysis is incomplete. Invalid requests return an error rather than a partial score.</p>
        <p>Zero is a numeric result; withheld is missing. A value of 100 means neither included pattern was observed in the eligible text. It never verifies authenticity, product quality or safety.</p>
        <p><strong>Public numeric scores are not approved.</strong> Before deployment, the release must withhold the score and present findings and coverage. Both API routes now withhold numeric scores, and the interface shows findings and coverage. The offline research baseline retains the experimental arithmetic; hosting and release approval remain pending.</p>
      </section>
      <section className="panel" aria-labelledby="method-validation">
        <h2 id="method-validation">Validation and known failures</h2>
        <p>No independent real electronics deception dataset has been admitted. The project chose not to train a model. Precision, recall, F1, confusion matrix, probability calibration and confidence levels are unavailable.</p>
        <p>Seventeen authored mechanical scenarios reproduce the implementation; they do not measure real-world accuracy. A fixed synthetic 40-row batch scores 50 overall, while its two halves score 0 and 100. Selecting reviews can change the result substantially.</p>
        <p>Local synthetic resource measurements do not establish hosted capacity. Unicode normalization can expand input and output substantially. Browser/provider budgets and security controls still require review before public release.</p>
        <p>Read supporting excerpts in context. Evidence is capped, and the interface identifies truncation; a displayed subset is not every matching row. Observed, unavailable and not-observed findings are reading states, not risk rankings.</p>
        <p>Use the <Link className="text-link" href="/contact">questions and disputes page</Link> for corrections or concerns when a contact destination is available.</p>
      </section>
      <Link className="text-link" href="/#analyze">Return to the analyzer →</Link>
    </main>
  );
}
