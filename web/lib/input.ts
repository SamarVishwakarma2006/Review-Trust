export const fields = ["text", "rating", "timestamp", "product_id", "source_id", "title", "verified_purchase"] as const;
export const MAX_BYTES = 1_048_576;
export const codePoints = (value: string) => Array.from(value).length;

// Header preview only. The API parses and validates every CSV record.
export function csvHeaders(source: string): string[] {
  const text = source.replace(/^\uFEFF/, "");
  const headers: string[] = [];
  let cell = "", quoted = false, closed = false;
  function finish() {
    const header = cell.trim();
    if (!header || codePoints(header) > 100 || headers.includes(header) || headers.length === 50 || header.includes("\0")) {
      throw new Error("Use 1–50 unique, nonempty headers of at most 100 characters.");
    }
    headers.push(header);
    cell = ""; closed = false;
  }
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (quoted) {
      if (char === '"') {
        if (text[i + 1] === '"') { cell += '"'; i++; }
        else { quoted = false; closed = true; }
      } else { cell += char; }
    } else if (char === ",") { finish(); }
    else if (char === "\n" || char === "\r") { finish(); return headers; }
    else if (char === '"' && cell === "" && !closed) { quoted = true; }
    else if (closed || char === '"') { throw new Error("The CSV header has malformed quotes."); }
    else { cell += char; }
  }
  if (quoted) throw new Error("The CSV header has an unclosed quote.");
  finish();
  return headers;
}

export function pasteBody(entries: string[]): string {
  const reviews = entries.map((text) => ({ text: text.trim() }));
  if (!reviews.length || reviews.length > 500 || reviews.some(({ text }) => !text || codePoints(text) > 5000)) {
    throw new Error("Enter 1–500 nonempty reviews, each at most 5,000 characters.");
  }
  if (reviews.reduce((sum, { text }) => sum + codePoints(text), 0) > 250_000) {
    throw new Error("Reviews must total at most 250,000 characters.");
  }
  const body = JSON.stringify({ schema_version: "1", category: "electronics", language: "en", origin: "paste", reviews });
  if (new TextEncoder().encode(body).length > MAX_BYTES) throw new Error("The encoded request exceeds 1 MiB. Reduce the input.");
  return body;
}
