import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "How it works | ReviewTrust" };

export default function HowItWorks() {
  return (
    <main id="content" tabIndex={-1} className="content-page">
      <header><p className="eyebrow">A guide to the analyzer</p><h1>How it works</h1><p className="intro">Start with a review subset. Finish with evidence you can inspect.</p></header>
      <section className="panel" aria-labelledby="supply-title">
        <h2 id="supply-title">1. Supply reviews you are permitted to use</h2>
        <p>Choose English-language reviews for one electronics product. Remove names, emails, phone numbers and other personal information. ReviewTrust does not fetch product pages or verify your product and language declarations.</p>
        <p>Paste one review per editable entry, or upload a UTF-8 CSV. Check the entry boundaries and keep duplicates if they are part of your source. Duplicate ingestion can itself explain repeated text.</p>
        <p>Limits: 500 reviews, 5,000 Unicode code points per text and 250,000 text/title code points in total. The API also enforces a 1 MiB request limit, including CSV multipart overhead. A file below one limit can still exceed another.</p>
      </section>
      <section className="panel" aria-labelledby="mapping-title">
        <h2 id="mapping-title">2. Check your fields and scope</h2>
        <p>CSV needs a header and a text column. Use the header mapping controls to select fields. Optional ratings, dates, titles and purchase flags can provide context; missing metadata stays missing. Malformed supplied metadata rejects the request instead of disappearing.</p>
        <p>The browser previews headers only. You can map headers before submission; the selected file is then sent to the API. Unmapped columns are discarded from canonical records by the server. Remove personal columns from the original file too: the upload bytes still include them.</p>
        <p>Confirm the English/electronics scope, then analyze. Validation errors identify safe row/field details so you can correct your input.</p>
      </section>
      <section className="panel" aria-labelledby="findings-title">
        <h2 id="findings-title">3. Inspect findings and gaps</h2>
        <p>Read the eligible and evaluated counts, then open the supporting-review disclosures. References such as r1 identify rows only within this request. Highlights show matched wording, not intent or conduct.</p>
        <p>Repetition and four listed incentive phrases feed the offline research index. Timing, rating distribution and conservative rating/text disagreement are contextual only. Unavailable methods explain their gaps; they do not count as evidence of low risk.</p>
        <p>Public numeric scores are always withheld. Small samples and low text coverage also create evidence gaps. There is no validated confidence level or trained authenticity model. Your selection can strongly change the findings and index.</p>
      </section>
      <section className="panel" aria-labelledby="clear-title">
        <h2 id="clear-title">4. Correct, cancel or clear</h2>
        <p>Edit input to discard previous results. Cancel stops the browser waiting; the server may finish bounded work before releasing its slot. Reset clears this interface. There is no saved analysis history or share link.</p>
        <p>Reset and normal memory cleanup do not guarantee secure erasure. See the <Link className="text-link" href="/privacy">privacy policy</Link> before submitting.</p>
      </section>
      <div className="actions"><Link className="button-link primary" href="/#analyze">Open the analyzer</Link><Link className="text-link" href="/methodology">Methodology and limitations →</Link></div>
    </main>
  );
}
