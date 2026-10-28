# Dataset audit — Step 7

Reviewed on 2026-10-27. Scope: published metadata, permission statements and target suitability. No third-party dataset archive was downloaded, no permission request was sent and no real review text was added. sources.json records the machine-readable decision and source references. A published download is not treated as an automatic permission grant.

| Candidate | Evidence from the primary source | ReviewTrust decision |
| --- | --- | --- |
| Amazon Reviews'23 Electronics | The release supplies an Electronics category and review text/rating/product/time metadata. The card declares English; no deception target is documented in that schema. [Release](https://amazon-reviews-2023.github.io/), [official card](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/blob/main/README.md). | Relevant domain, but ratings/verified purchase cannot supply deception labels. Actual subset language, missingness and duplicates are unmeasured. Candidate for future descriptive evaluation only after rights review. |
| Amazon permission statement | A lab maintainer states they cannot assign a dataset licence and describes research availability. A later reply concerns a particular thesis. [Maintainer discussion](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/discussions/1). | ReviewTrust use, commercial use, redistribution and excerpt permission remain unestablished; do not infer a licence from mirrors or another person's approval. Admission: not_approved. |
| YelpCHI | The maintainer describes Chicago hotel/restaurant reviews with text, ratings, dates and identifiers; labels derive from recommended/filtered status. It reports 13.23% filtered and asks prospective users to email for access. [Maintainer page](https://shebuti.com/yelpchi-dataset/). | Domain mismatch and proxy target. The inspected page gives no explicit reuse licence. ReviewTrust access/redistribution/excerpt rights are unestablished. Admission: not_approved. No local class/missingness/duplicate measurements. |
| Ott et al. ACL 2011 | The study pairs prompted fictitious hotel reviews with presumed truthful TripAdvisor reviews; it reports 400 in each group. [Study](https://aclanthology.org/P11-1032.pdf). | Hotels, elicitation and historical collection differ from electronics deployment. These are study-protocol labels; no transfer of published accuracy is claimed. Dataset reuse/excerpt rights were not established. Archive quality is unmeasured; later v1.4 was not inspected. Admission: not_approved. |

These are project admission decisions based on the inspected evidence, not legal certifications or claims that a dataset is prohibited for every use. Publisher-reported numbers are not local measurements. Missing class balance for unlabeled Amazon data is not an invented zero-deception rate. Terms and releases must be rechecked when an acquisition is proposed.

## Required admission record for future data

Before acquiring or admitting real data, record the exact release/revision and origin, collection method/date range, category/language evidence, privacy minimization, permitted purpose, use/redistribution/excerpt restrictions, supporting permission source and reviewer/date. Keep a hash of the exact authorized source artifact and preprocessing code/version. Separate the original artifact from normalized records and record every exclusion with a fixed reason and count; do not silently drop malformed rows.

Document each label's meaning, origin and uncertainty. Platform filtering, star ratings, helpfulness, verified purchase and detector outputs cannot be relabelled as independent deception truth. Define electronics relevance and sampling/source/time shifts before drawing a subset. Profile class/support counts, missing fields, text lengths, exact/near duplicates and conflicts on the actual admitted subset. Keep the whole product/duplicate graph together across partitions, and record ratios/seed/IDs/hash before training. A tiny or giant connected component can make an experiment unusable; record that outcome instead of weakening grouping to obtain convenient splits.

The current code intentionally has no real-data admission override. Accepting a real corpus requires a reviewed code/source-card change and regression fixtures under a new research pipeline version. This avoids treating an arbitrary edited JSON permission flag as authorization. The deployed scoring methodology remains rt-patterns-0.2.0-experimental.

## Measured synthetic mechanics

The project-authored fixture contains 24 rows, 12 product groups and one exact cross-product duplicate. Product plus duplicate connections yield 11 components; largest size 4. Ratings are missing in 8 rows and dates in 6. Scenario labels have 12 rows per class; these are authored test scenarios, not verified deception cases. Seed 20261027 assigns 20 train, 2 validation and 2 test rows. Each partition happens to contain both scenario labels; the split algorithm does not use labels. No cross-partition product or detected duplicate component is present in tests. Separate tests exercise transitive near matches and abstention.

The committed synthetic manifest freezes all row assignments and hashes. Reproduce with ml/README.md commands; generated outputs are ignored. These figures validate audit mechanics only. Generalization, full-corpus leakage, privacy, resource performance and real-world label validity have not been established.

## Step 8 input

No approved in-domain deception target exists after this audit. Step 8 must explicitly assess the no-train path and use justified heuristic/mechanical evaluation unless new evidence resolves both permissions and target validity. Synthetic fixtures cannot justify classifier training, probability calibration, confidence levels or an authenticity-accuracy claim. This handoff is an audit result; it does not execute Step 8 or select a model.

Step 8 follow-up (2026-10-28): [model card](MODEL_CARD.md) records NO TRAIN and [evaluation record](EVALUATION.md) documents the mechanical baseline checks. The original audit evidence and source cards remain frozen.
