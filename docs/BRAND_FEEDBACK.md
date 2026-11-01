# E15 synthetic brand feedback

Owner approved three distinct authored headphone models, fixed catalog order and
sample-level wording on 2026-11-01. The synthetic implementation is complete;
real-source acceptance still requires source access and verified identity evidence.

The demo endpoint accepts brand and brand_gaps. It reuses E14's bounded analysis
and returns the optional literal brand label "Example (authored brand)". That label
declares this fixed catalog only: H0/H1/H2, brand Example, seller example-seller,
manufacturer unknown. It is not a generic brand resolver or seller-based inference.
The client rejects other labels, unexpected model titles/counts and invalid assembly
windows before rendering the fixed brand view. Other comparison scenarios retain a
null brand label. No submitted brands, URLs or external requests are supported.

The view counts product samples containing assessed negative wording for each
existing feedback aspect. Each product counts once regardless of review volume;
the denominator includes all three selected models, including missing samples.
It identifies the models and retains per-product evidence disclosures. It does not
pool ratings, label a company good/bad/genuine, infer independent incidents or
interpret unassessed/no-negative wording as positive evidence. The catalog selection
is biased and not representative. Assembly timestamps are not publication dates;
publication dates and real-world totals remain explicitly unknown.

The browser groups identical displayed masked review bodies across products and
lists model/local-review references. Repeated rows remain in their original samples.
Only exact body text is compared; paraphrases, title differences, ownership and
reviewer identity are not resolved. Groups are not independent supporting incidents.
The existing three-product/40-row demo ceiling bounds this work. No new dependency,
storage, model, source admission, score, deadline or public endpoint was introduced.

Verification: full scripts/check.ps1 passed: 500 backend, 28 offline, 35 frontend
tests, pip consistency, Ruff, ESLint, types and production build. Browser exercised
brand_gaps through the local API: 2/3 reviewed samples, 2/3 battery-negative samples,
missing/partial coverage and two shared-text groups. Existing frozen reports passed
unchanged; they do not benchmark this presentation path. Live-source E15 remains
pending. Next E16 is an admission/no-train review, not automatic training permission.
