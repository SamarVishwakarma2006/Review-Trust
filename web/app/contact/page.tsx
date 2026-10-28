import type { Metadata } from "next";
import Link from "next/link";
import { CONTACT_EMAIL } from "../../lib/contact";

export const metadata: Metadata = { title: "Questions and disputes | ReviewTrust" };

export default function Contact() {
  const email = CONTACT_EMAIL.trim();
  return (
    <main id="content" tabIndex={-1} className="content-page">
      <header><p className="eyebrow">Questions, corrections and disputes</p><h1>Contact ReviewTrust</h1><p className="intro">Findings can miss context. A review pattern does not establish misconduct.</p></header>
      <section className="panel" aria-labelledby="contact-title">
        <h2 id="contact-title">Contact address</h2>
        <div className="contact-address" aria-label="Contact email address">
          {email ? <a className="text-link" href={`mailto:${encodeURIComponent(email)}?subject=ReviewTrust%20question%20or%20dispute`}>{email}</a> : <span aria-label="No contact address configured">&nbsp;</span>}
        </div>
        {email ? <p>This link opens your email application. ReviewTrust does not send a message automatically or receive it through this website.</p> : <p>A contact address has not been added yet. Questions and disputes cannot be sent through this page until the site owner adds one.</p>}
        <p>This website has no contact form, ticket storage or automatic response. No response time or resolution is guaranteed.</p>
      </section>
      <section className="panel" aria-labelledby="dispute-title">
        <h2 id="dispute-title">What to include when a destination is available</h2>
        <ul>
          <li>The methodology version and the finding or explanation you want reviewed.</li>
          <li>A request ID if one was displayed, and a short description of what happened. A request ID does not retrieve a stored analysis.</li>
          <li>Relevant context or a minimal example with personal information removed. Do not send original review files, reviewer identities, credentials or private purchase details.</li>
        </ul>
        <p>Explain whether you are reporting a technical error, missing context, an accessibility issue or a concern about interpretation. Avoid public accusations based on an experimental result.</p>
        <p>Email uses your chosen provider and the recipient’s mailbox. Their retention and access practices are separate from in-memory analysis. See our <Link className="text-link" href="/privacy">privacy policy</Link>.</p>
      </section>
      <Link className="text-link" href="/methodology">Review the methodology and limits →</Link>
    </main>
  );
}
