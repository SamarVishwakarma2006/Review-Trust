import type { Metadata } from "next";
import Link from "next/link";
import { CONTACT_EMAIL } from "../../lib/contact";

export const metadata: Metadata = { title: "Privacy policy | ReviewTrust" };

export default function Privacy() {
  return (
    <main id="content" tabIndex={-1} className="content-page">
      <header><p className="eyebrow">Development privacy policy</p><h1>Your input and its boundaries.</h1><p className="intro">Remove personal information before submitting. Automatic masking is incomplete.</p><p>Updated 28 October 2026. This policy describes the current development implementation. Hosting providers, their logs and retention must be verified and this policy updated before public deployment.</p></header>
      <section className="panel" aria-labelledby="privacy-data">
        <h2 id="privacy-data">What you supply</h2>
        <p>Pasted review text or a selected CSV may include optional ratings, timestamps, titles, purchase flags and product/source identifiers. Submit only content you are permitted to use. Do not include reviewer names, contact details, credentials, private purchase details or other personal information.</p>
        <p>The browser reads the selected CSV into memory to preview headers and mapping. When you choose Analyze, it uploads the file bytes, including unmapped columns, to the configured analysis API. The API discards unmapped columns from canonical review records; remove sensitive columns before choosing the file.</p>
      </section>
      <section className="panel" aria-labelledby="privacy-flow">
        <h2 id="privacy-flow">Where analysis happens</h2>
        <p>The browser sends your submission directly to the configured FastAPI origin. Next.js serves the interface and does not proxy the analysis. Common emails and phone numbers are masked in analyzed and returned text, but raw upload bytes reach the API first. Names and other personal details can remain in excerpts.</p>
        <p>Input and results are held in application memory. The implementation does not save uploads to disk, create a database, store analysis history, use browser localStorage or send review content to a paid LLM. There are no accounts, advertising or analytics integrations, or product-page fetching.</p>
        <p>Analysis and error responses request no caching. Application code does not log raw review bodies; unexpected API failures log only a fixed error code and request ID. Infrastructure and access logs are a separate deployment concern.</p>
      </section>
      <section className="panel" aria-labelledby="privacy-metadata">
        <h2 id="privacy-metadata">Connection information and limits</h2>
        <p>Serving the site and API requires processing network connection information. The API’s in-memory rate limiter uses a process-scoped hash of the peer address, with bounded entries and idle expiry. This is not a promise of anonymous use.</p>
        <p>Production hosting, proxy headers, provider access logs, log retention and provider access have not been approved or verified. We cannot promise that hosting infrastructure records nothing. Deployment is pending those reviews.</p>
      </section>
      <section className="panel" aria-labelledby="privacy-clear">
        <h2 id="privacy-clear">Clearing and correcting input</h2>
        <p>Reset clears the analyzer’s input and result state, including the selected file and mapping. Editing discards previous results. Cancel stops the browser waiting, but server work may continue within its execution budget before cleanup.</p>
        <p>Ordinary memory cleanup and closing a page are not secure-erasure guarantees. Browser navigation, caches outside application control, operating-system memory and crash handling can differ. No server history exists for retrieving or deleting a past analysis through this application.</p>
      </section>
      <section className="panel" aria-labelledby="privacy-contact">
        <h2 id="privacy-contact">Questions and email</h2>
        <p>The <Link className="text-link" href="/contact">contact page</Link> shows whether a destination is configured. {CONTACT_EMAIL.trim() ? "A contact email link is available there." : "No address has been supplied for this development preview. Contact and dispute submission remain unavailable until the owner adds one."}</p>
        <p>If an email address is added, following its link opens your email application. Sending is your choice and uses your provider and the recipient’s mailbox, outside the analyzer’s in-memory flow. Email may be retained by those services; no mailbox retention policy or response time is established here. Avoid sending raw review files or personal information.</p>
      </section>
    </main>
  );
}
