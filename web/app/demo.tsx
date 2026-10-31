"use client";
import { useEffect, useRef, useState } from "react";
import { apiBase } from "../lib/api";
import { isDemo, type DemoResult } from "../lib/demo";

export default function Demo() {
  const [example, setExample] = useState("patterns");
  const [result, setResult] = useState<DemoResult | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const current = useRef<AbortController | null>(null);
  useEffect(() => () => current.current?.abort(), []);
  function cancel() { current.current?.abort(); current.current = null; setBusy(false); setResult(null); setMessage(""); }
  async function run() {
    cancel();
    const controller = new AbortController(); current.current = controller;
    setBusy(true); setMessage("Analyzing authored examples…");
    try {
      const response = await fetch(`${apiBase()}/v2/demo/analyze`, { method: "POST", credentials: "omit", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ example }), signal: controller.signal });
      if (!response.ok) throw new Error(response.status === 429 ? "Please wait before running another demo." : "The demo API is unavailable. Check the local API server and try again.");
      const data: unknown = await response.json();
      if (!isDemo(data)) throw new Error("The demo returned an unsupported result.");
      if (current.current === controller) { setResult(data); setMessage("Synthetic example analyzed. No website was crawled."); }
    } catch (error) { if (current.current === controller && !controller.signal.aborted) setMessage(error instanceof Error ? error.message : "Demo request failed."); }
    finally { if (current.current === controller) { setBusy(false); current.current = null; } }
  }
  return <section className="panel" id="demo" aria-labelledby="demo-heading">
    <p className="eyebrow">Synthetic demo · No live collection</p>
    <h2 id="demo-heading">Try a product review example</h2>
    <p>Explore the planned product-analysis experience using reviews authored for this demo. These are not real products or customer reviews. Product-link crawling is not available yet.</p>
    <label htmlFor="demo-example">Choose an authored example</label>
    <select id="demo-example" value={example} onChange={e => { cancel(); setExample(e.target.value); }}>
      <option value="patterns">Headphones — repeated wording and incentive mentions</option>
      <option value="partial">Headphones — incomplete review sample</option>
      <option value="empty">Headphones — no reviews in the example</option>
    </select>
    <div className="actions"><button className="primary" disabled={busy} onClick={run}>Analyze synthetic example</button><button onClick={cancel}>{busy ? "Cancel demo" : "Reset demo"}</button></div>
    <p role="status">{message}</p>
    {result && <div aria-label="Synthetic demo result">
      <h3>{result.product_title}</h3>
      <p><strong>Authored synthetic data.</strong> {result.analyzed_reviews} reviews analyzed. Example coverage: {result.status}. Total real-world reviews: unknown.</p>
      <p>Numeric score and confidence are withheld. This does not establish authenticity or product quality.</p>
      {result.status === "partial" && <p>This example intentionally stops before exhaustion. The sample does not represent all reviews.</p>}
      {!result.analysis ? <p>No reviews are available in this example; there is no analysis.</p> : result.analysis.findings.map((finding, i) => <div className="finding" key={i}><h4>{finding.signal_id.replaceAll("_", " ")}</h4><p>{finding.assessment.replaceAll("_", " ")}: {finding.explanation}</p></div>)}
    </div>}
  </section>;
}
