# Labelling protocol — rt-labels-0.1

The initial dataset audit admits synthetic test scenarios only. This protocol makes label decisions explicit; it does not establish deception from text style. No real annotation round has occurred and no human agreement statistic is claimed.

## Target and uncertainty

A future supervised target must describe a precisely documented study outcome supported by external evidence. A deceptive label requires documented intentionally fictitious review conduct under the declared protocol. A non_deceptive label requires documented control/provenance appropriate to that protocol; absence of a red flag, purchase verification or plausible prose is insufficient. Neither label is a universal authenticity certification. If evidence does not support the target, record unknown and do not train. Sentiment and platform-filtering proxies remain separate bases, never target substitutions.

Annotation sources may include released study instructions or independently documented case provenance when rights and scope are established. Evidence must be reviewed for permission, privacy, applicability to this exact row and remaining uncertainty. Do not copy personal material into a public ledger. Use an opaque hash reference to a restricted local evidence record with release/revision, rubric version, scope, reviewer role and reason. Hashing does not itself establish permission, truth or independence.

## Review procedure

1. Freeze the permitted artifact, sampling rule and rubric before annotation. Define target classes and exclusion rules without seeing test outcomes.
2. Assign two independent reviewers experiment roles a1 and a2, with separate initial decisions. Do not expose detector score, proxy labels, the other vote or intended partition during review. The current code validates distinct role codes, not actual reviewer independence.
3. Each vote records decision (deceptive/non_deceptive/unknown), basis and evidence_ref. No names or free-form private notes enter normalized JSONL. At most three role-coded votes are accepted. No votes, unsupported bases, missing evidence, any unknown vote or a disagreement resolve to unknown.
4. Consensus requires at least two distinct role votes with the same supported decision, each citing reviewed evidence. In synthetic fixtures only synthetic_scenario is supported; an external_documentation branch exists for protocol unit mechanics but the CLI does not admit real corpora. A matching pair of proxy votes still resolves unknown.
5. Disagreements remain unknown pending a separate documented adjudication; never silently overwrite votes. A revised ledger requires a new source/annotation artifact version and manifest. Adding a third vote does not create a majority shortcut: all recorded votes must agree under the current rule. Keep initial votes for later agreement/error analysis under approved local retention.
6. Report class counts, unknown/conflict counts and basis coverage. On real annotation work compute actual reviewer agreement and a blinded adjudicated sample only after recording the round; do not invent agreement from synthetic votes.

## Normalized vote shape

```json
{
  "annotator": "a1",
  "decision": "unknown",
  "basis": "unknown",
  "evidence_ref": null
}
```

Other bases: synthetic_scenario, external_documentation, sentiment_proxy, platform_proxy. A non-null evidence_ref is 64-character lowercase hex and identifies a separately reviewed local evidence artifact. A record may have an empty votes list. Raw source labels must retain their original meaning and provenance before any mapping; transformation code and reasons must be recorded. ReviewTrust's public analysis input does not accept annotations.

## Split and training discipline

Resolve labels without using them to place records. Join products and detected exact/near duplicate components before train/validation/test assignment; current bounded mechanics are in ml/README.md. Split diagnostics and unknown labels block use of that split as a complete binary supervised experiment. Real data require broader provenance, group-mapping and time/source-shift review than this synthetic harness.

Freeze test membership before feature fitting. Fit learned text preprocessing/vocabulary on training only; tune on validation only. Held-out labels do not justify test-set-driven feature/threshold selection. Changing labels or split policy invalidates the previous manifest; create a documented new experiment rather than updating test IDs quietly. Published or synthetic labels alone cannot authorize model training: permission, target validity, scope and usable support all remain separate gates.
