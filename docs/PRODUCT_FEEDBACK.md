# E09 product feedback preparation

Date: 2026-11-01. Status: OFFLINE EXTRACTOR IMPLEMENTED; demo integration and evaluation pending.
Owner deferred Bright Data setup and requested the next step. This permits
independent E09 preparation; it does not complete the live-source gates.

## Proposed first scope

English headphone/earphone reviews. Four aspects: battery, comfort, durability
and sound. Use a small deterministic method, with no LLM or training dependency.
Keep this feedback separate from review-pattern findings and withheld scores.
The offline feedback version is `rt-feedback-0.1.0`, implemented in
api/app/product_feedback.py. SPEC.md remains authoritative for current HTTP contracts.
The extractor accepts only pipeline display records that are already validated
and masked; it is not a public ingestion function. Ten authored regression cases
pass, covering attribution, abstention, mixed wording, caps, Unicode spans and deadlines.

## Extraction contract for implementation

Operate only on validated, normalized, masked review bodies. Exclude titles and
ratings from polarity inference. Match whole-word aspect terms, case-insensitively:
battery (`battery`, `batteries`), comfort (`comfort`, `comfortable`, `uncomfortable`),
durability (`durability`, `durable`, `broke`, `broken`), sound (`sound`, `audio`).
A mention alone is neither praise nor a complaint.

The initial polarity recognizer should accept only explicit whole clauses:
`[the ]battery is good|bad`, `[the ]sound is good|bad`,
`[the ]audio is good|bad`, `these headphones are comfortable|uncomfortable`,
`these earphones are comfortable|uncomfortable`,
`these headphones are durable|broken`, and `these earphones are durable|broken`.
Bracketed articles are optional; whitespace may vary. Split clauses only at
period, question mark, exclamation mark or newline. Trim clause whitespace.
Other wording remains unassessed. Match complete clauses, never a substring
inside negation, comparison, quotation, instructions or conditional wording.
Conservatively abstain from polarity for the entire review if it contains quote
characters, negation tokens (`no`, `not`, `never`, `n't`), or ambiguity tokens
(`if`, `but`, `although`, `however`, `wish`, `sarcasm`). Mention counts remain.
These rules intentionally have low recall and cannot detect all sarcasm.

Count each review once per aspect. Aggregate each mentioned aspect into exactly
one of positive, negative, mixed (both supported polarities), or unassessed.
Mixed is descriptive disagreement within a review, not a quality verdict.
For every aspect, require:
`positive + negative + mixed + unassessed = mentioned <= analyzed_reviews`.
Zero mentions means no evidence; zero analyzed reviews means summary unavailable.
Repeated wording across distinct reviews stays in the denominator, with the
existing repetition limitation visible; do not call the reviews independent.

## Evidence and presentation

Return aspect ID, version, analyzed/mentioned counts, the four assessment counts,
and bounded supporting request-local references. Keep at most three evidence
references per assessment per aspect in input order; include omitted counts.
Evidence spans must refer to the actual masked display text using Unicode code
points, exclusive end. Reuse returned reviews rather than copying bodies into
another response field. Never fabricate or silently truncate a quote.

Suggested copy: "Battery mentioned in 4 of 20 sampled reviews: 2 supported
positive statements, 1 negative statement, 1 unassessed mention."
Always retain synthetic labels or actual source/sample provenance, partial
coverage, selection order and unknown totals. A top-review sample cannot imply
newest reviews or represent all buyers. Counts describe reported wording, not
verified product performance. Do not label a product good, fake or authentic.

## Authored acceptance cases to implement

| Body | Expected battery result |
| --- | --- |
| The battery is good. | mentioned, positive |
| The battery is bad. | mentioned, negative |
| Battery included. | mentioned, unassessed |
| The battery is not good. | mentioned, unassessed |
| If the battery is good, I will buy it. | mentioned, unassessed |
| "The battery is good." | mentioned, unassessed |
| The battery is good. The battery is bad. | mentioned once, mixed |
| The battery is good. The battery is good. | mentioned once, positive |
| Batterylife is good. | no mention under this vocabulary |
| Sound is good. Battery included. | battery unassessed; sound positive |

Also check all four aspects, empty/partial samples, repeated review rows,
Unicode offsets, masked contact strings, escaped markup, evidence caps and
deadline/response limits. Do not derive sentiment from star ratings.

## Completion path

Next integrate the pure extractor and authored regression cases
into the explicitly synthetic demo with typed API/browser validation. Keep
current v1 contracts stable; intentionally review any changed source-bound
mechanics/benchmark records. Run relevant checks and browser demonstration.

Full E09 acceptance additionally requires a permitted, human-reviewed sample
with independently recorded aspect/polarity/unknown annotations and documented
errors and abstention coverage. Establish evaluation criteria before examining
its outcomes. Authored cases prove mechanics only. Real-source use remains
pending E02/E05 and collected API integration; no dataset is admitted here.
