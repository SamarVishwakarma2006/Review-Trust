import Analyzer from "./analyzer";
import Link from "next/link";

export default function Home() {
  return (
    <main id="content" tabIndex={-1}>
      <header className="hero">
        <div>
        <p className="eyebrow">Electronics · English · Experimental</p>
        <h1>Look closer at the reviews.</h1>
        <p className="intro">Explore shared wording, incentive mentions and missing evidence in the reviews you supply.</p>
        <p>ReviewTrust explains observable patterns in an English-language review subset for one electronics product. Patterns are not proven deception.</p>
        <div className="actions">
          <a className="button-link primary" href="#analyze">Analyze your reviews</a>
          <Link className="text-link" href="/how-it-works">See how it works →</Link>
        </div>
        </div>
        <aside className="hero-note" aria-labelledby="read-evidence">
          <p className="eyebrow">Read the evidence</p>
          <h2 id="read-evidence">A pattern is a starting point.</h2>
          <p>Shared wording can come from a supplied template or duplicate ingestion. A burst of reviews can follow a legitimate launch.</p>
          <p>Inspect the supporting text and coverage before drawing a conclusion. Missing evidence is a gap, never a low-risk finding.</p>
          <Link className="text-link" href="/methodology">Understand the limits →</Link>
        </aside>
      </header>
      <section className="before-analysis" aria-labelledby="prepare-title">
        <h2 id="prepare-title">Before you begin</h2>
        <ol className="steps-grid">
          <li><h3>Choose one product</h3><p>Use English reviews for one electronics product. Your selection may not represent all its reviews.</p></li>
          <li><h3>Remove personal details</h3><p>Remove names and contact details first. Automatic masking is incomplete.</p></li>
          <li><h3>Read findings with context</h3><p>Review counts, supporting excerpts and unavailable methods together. This is not a purchasing recommendation.</p></li>
        </ol>
      </section>
      <div id="analyze" className="analyzer-anchor" tabIndex={-1}><Analyzer /></div>
      <section className="panel limitations" aria-labelledby="release-title">
        <h2 id="release-title">An experimental development preview</h2>
        <p>The analyzer returns findings and coverage with numeric scores withheld. It is not a probability that reviews are genuine, a product-quality rating or validated confidence. A value of 100 does not verify authenticity.</p>
        <p>Public numeric scores are not approved. Before public deployment, the release must withhold the score and show findings and coverage. Both API routes and this interface now enforce withholding. Production configuration and release approval remain pending.</p>
        <p><Link className="text-link" href="/methodology">Read the methodology</Link> or <Link className="text-link" href="/privacy">learn what happens to your input</Link>.</p>
      </section>
    </main>
  );
}
