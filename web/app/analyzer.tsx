"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { analyze, type AnalysisResult } from "../lib/api";
import { csvHeaders, fields, MAX_BYTES, pasteBody } from "../lib/input";
import Results from "./results";

export default function Analyzer() {
  const [mode, setMode] = useState<"paste" | "csv">("paste");
  const [entries, setEntries] = useState([""]);
  const [file, setFile] = useState<File | null>(null);
  const [headers, setHeaders] = useState<string[]>([]);
  const [mapping, setMapping] = useState<string[]>([]);
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [reading, setReading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const request = useRef<AbortController | null>(null);
  const generation = useRef(0);
  const fileInput = useRef<HTMLInputElement>(null);
  const feedback = useRef<HTMLDivElement>(null);
  const firstInput = useRef<HTMLTextAreaElement>(null);
  const addButton = useRef<HTMLButtonElement>(null);

  useEffect(() => () => { generation.current++; request.current?.abort(); }, []);
  useEffect(() => { if (error || result) feedback.current?.focus(); }, [error, result]);

  function invalidate() {
    generation.current++;
    request.current?.abort(); request.current = null;
    setBusy(false); setReading(false); setResult(null); setError(""); setNotice("");
  }
  function reset() {
    invalidate(); setEntries([""]); setFile(null); setHeaders([]); setMapping([]); setConfirmed(false);
    if (fileInput.current) fileInput.current.value = "";
    setNotice("Input and results cleared.");
    if (mode === "paste") firstInput.current?.focus(); else fileInput.current?.focus();
  }
  async function selectFile(selected: File | undefined) {
    invalidate(); setFile(null); setHeaders([]); setMapping([]);
    if (!selected) return;
    const current = generation.current;
    setReading(true);
    try {
      if (!selected.size || selected.size > MAX_BYTES) throw new Error("Select a nonempty UTF-8 CSV smaller than 1 MiB; the multipart envelope also counts toward the API limit.");
      // Bounded read, header-only preview. Fatal decoding prevents silent replacement characters.
      const buffer = await selected.arrayBuffer();
      const parsed = csvHeaders(new TextDecoder("utf-8", { fatal: true }).decode(buffer));
      if (current !== generation.current) return;
      setHeaders(parsed); setMapping(parsed.map(h => fields.find(f => f === h) || "")); setFile(selected);
    } catch (e) {
      if (current === generation.current) setError(e instanceof TypeError ? "The file could not be read as UTF-8 CSV." : e instanceof Error ? e.message : "Could not read the file.");
    } finally { if (current === generation.current) setReading(false); }
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (request.current || reading) return;
    invalidate();
    const current = generation.current;
    let body: string | FormData;
    try {
      if (!confirmed) throw new Error("Confirm English reviews for one electronics product before submitting.");
      if (mode === "paste") body = pasteBody(entries);
      else {
        if (!file) throw new Error("Select a CSV and map its review text column.");
        const selected = mapping.filter(Boolean);
        if (!selected.includes("text") || new Set(selected).size !== selected.length) throw new Error("Map exactly one column to text; each other field may be mapped only once.");
        const mapped = Object.fromEntries(headers.flatMap((h, i) => mapping[i] ? [[h, mapping[i]]] : []));
        const mappingJson = JSON.stringify(mapped);
        if (new TextEncoder().encode(mappingJson).length > 4096) throw new Error("The column mapping exceeds 4,096 bytes. Shorten the CSV headers.");
        body = new FormData();
        // Fixed filename avoids sending local filenames, which can contain personal data.
        body.append("file", file, "reviews.csv");
        body.append("schema_version", "1"); body.append("category", "electronics"); body.append("language", "en");
        body.append("mapping", mappingJson);
      }
    } catch (e) { setError(e instanceof Error ? e.message : "Check your input."); return; }
    const controller = new AbortController(); request.current = controller; setBusy(true);
    const timeout = window.setTimeout(() => {
      if (current !== generation.current) return;
      invalidate(); setError("The request took too long. The server may still be finishing bounded work; try again later.");
    }, 35_000);
    try {
      const response = await analyze(body, controller.signal);
      if (current === generation.current) setResult(response);
    } catch (e) {
      if (current === generation.current) setError(e instanceof Error ? e.message : "Analysis failed. Try again.");
    } finally {
      window.clearTimeout(timeout);
      if (current === generation.current) { request.current = null; setBusy(false); }
    }
  }

  return <>
    <section aria-labelledby="input-title" className="panel">
      <h2 id="input-title">Analyze a review subset</h2>
      <p>Remove names, email addresses, phone numbers and other personal information before submitting. Automatic masking is incomplete.</p>
      <p className="muted">Input and results stay in application memory; no saved history. Reset clears this view. This development app is not approved for public deployment.</p>
      <form onSubmit={submit}>
        <fieldset disabled={busy}>
          <legend>Input method</legend>
          <div className="actions">
            <label><input type="radio" name="mode" checked={mode === "paste"} onChange={() => { invalidate(); setMode("paste"); }} /> Paste reviews</label>
            <label><input type="radio" name="mode" checked={mode === "csv"} onChange={() => { invalidate(); setMode("csv"); }} /> Upload CSV</label>
          </div>
          {mode === "paste" ? <>
            <p id="paste-help">One review per entry. Duplicates are kept. Up to 500 reviews, 5,000 characters each and 250,000 total. Optional metadata can be supplied through CSV.</p>
            <p><strong>{entries.length} review {entries.length === 1 ? "entry" : "entries"}</strong> — check the boundaries before submitting.</p>
            {entries.map((entry, i) => <div className="entry" key={i}>
              <label htmlFor={`entry-${i}`}>Review {i + 1}</label>
              <textarea id={`entry-${i}`} ref={i === 0 ? firstInput : undefined} rows={3} value={entry} aria-describedby="paste-help" onChange={e => { invalidate(); setEntries(entries.map((v, n) => n === i ? e.target.value : v)); }} />
              {entries.length > 1 && <button type="button" onClick={() => { invalidate(); setEntries(entries.filter((_, n) => n !== i)); addButton.current?.focus(); }}>Remove review {i + 1}</button>}
            </div>)}
            <button ref={addButton} type="button" disabled={entries.length >= 500} onClick={() => { invalidate(); setEntries([...entries, ""]); }}>Add review</button>
          </> : <>
            <label htmlFor="csv-file">UTF-8 CSV file</label>
            <input ref={fileInput} id="csv-file" type="file" accept=".csv,text/csv" onChange={e => { void selectFile(e.target.files?.[0]); }} />
            <p>Header required; commas and standard quoted fields supported. At most 1 MiB including the upload envelope. No rows are dropped or truncated. CSV error rows include the header as record 1.</p>
            {headers.length > 0 && <div className="mapping">
              <h3>Map columns</h3>
              <p>Only the header is previewed. Map text once; optional fields are validated by the API. Unmapped columns are ignored.</p>
              {headers.map((h, i) => <label key={i}>Column {i + 1}: {h}
                <select value={mapping[i]} onChange={e => { invalidate(); setMapping(mapping.map((v, n) => n === i ? e.target.value : v)); }}>
                  <option value="">Ignore column</option>
                  {fields.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </label>)}
            </div>}
          </>}
          <label className="confirmation"><input type="checkbox" checked={confirmed} onChange={e => { invalidate(); setConfirmed(e.target.checked); }} /> I confirm these are English reviews for one electronics product. This subset may not represent all reviews.</label>
          <button className="primary" type="submit" disabled={reading}>{busy ? "Analyzing…" : "Analyze reviews"}</button>
        </fieldset>
        <div className="actions">
          {busy && <button type="button" onClick={() => { invalidate(); setNotice("Request canceled. Server work may finish within its existing budget."); }}>Cancel analysis</button>}
          <button type="button" onClick={reset}>Reset input and results</button>
        </div>
      </form>
      <p role="status">{busy ? "Analyzing the submitted subset…" : reading ? "Reading CSV header…" : notice}</p>
    </section>
    <div ref={feedback} tabIndex={-1}>
      {error && <section role="alert" className="panel error"><h2>Analysis could not complete</h2><p>{error}</p><p>Your input is retained for correction. No partial score is shown.</p></section>}
      {result && <Results result={result} />}
    </div>
  </>;
}
