import type { Comparison } from "./comparison";

/** Counts product samples, never buyers or independent incidents. Exact masked text only. */
export function brandEvidence(products: Comparison["products"]) {
  const groups = new Map<string, { product: number; ref: string }[]>();
  products.forEach((p, product) => p.report.analysis?.reviews.forEach(r => {
    const members = groups.get(r.text) ?? [];
    members.push({ product, ref: r.ref });
    groups.set(r.text, members);
  }));
  return {
    reviewed: products.filter(p => p.report.analyzed_reviews > 0).length,
    issues: ["battery", "comfort", "durability", "sound"].map(aspect => ({
      aspect,
      products: products.flatMap((p, i) => p.report.feedback?.aspects.some(a => a.aspect === aspect && a.counts.negative > 0) ? [i] : []),
    })),
    shared: [...groups.values()].filter(members => new Set(members.map(m => m.product)).size > 1),
  };
}
