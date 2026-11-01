import type { Comparison } from "../lib/comparison";
import { brandEvidence } from "../lib/brand";

export default function BrandView({ result }: { result: Comparison }) {
  const evidence = brandEvidence(result.products);
  return <section aria-label="Synthetic brand feedback">
    <h3>Feedback across {result.brand}</h3>
    <p>Authored synthetic catalog: H0, H1 and H2 are three distinct headphone models explicitly assigned to this example brand. Selected in fixed catalog order, not by ratings or complaints. This small selection does not represent a brand catalog.</p>
    <p>Brand: Example (authored). Seller: example-seller (authored listing identity). Manufacturer: unknown. A shared seller does not establish a shared brand or manufacturer.</p>
    <p>{evidence.reviewed} of {result.products.length} selected product samples contain reviews. Missing samples and unassessed wording are unknown, not positive evidence. There is insufficient evidence for a company-wide quality or authenticity conclusion. Ratings are not pooled.</p>
    <ul>{result.products.map((p, i) => <li key={i}>H{i}: {p.report.analyzed_reviews} rows, {p.report.status}. Assembly window: {p.report.window_started_at} to {p.report.window_finished_at}. Review publication dates and real-world totals are unknown.</li>)}</ul>
    <h4>Reported negative wording across samples</h4>
    {evidence.issues.map(issue => <p key={issue.aspect}>{issue.aspect}: {issue.products.length ? `reported in samples from ${issue.products.length} of ${result.products.length} selected products (${issue.products.map(i => `H${i}`).join(", ")}).` : "No assessed negative wording in these samples; this does not establish absence of problems."}</p>)}
    <h4>Shared wording limits independence</h4>
    <p>{evidence.shared.length} exact displayed-text groups span more than one product. Repeated rows remain in each product sample; product counts above do not count independent incidents. Only exact masked body text is checked here, not paraphrases, reviewer identity or ownership.</p>
    {evidence.shared.map((members, i) => <details key={i}><summary>Shared wording group {i + 1}: {members.length} rows across {new Set(members.map(m => m.product)).size} products</summary><p>{members.map(m => `H${m.product}/${m.ref}`).join(", ")}</p></details>)}
    <p>Inspect each product’s feedback disclosures below for the supporting wording and omitted-evidence counts. Different sample sizes, unknown review dates and repeated text prevent treating this as independent brand-performance evidence.</p>
  </section>;
}
