import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import Demo from "../app/demo";
import { isDemo } from "../lib/demo";
const empty = { schema_version: "2", ingestion_version: "rt-fixture-analysis-0.1.0", evidence_origin: "authored_fixture", status: "empty", product_title: "Synthetic headphones", analyzed_reviews: 0, analysis: null };
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
test("demo requests a fixed example and renders explicit synthetic empty state", async () => {
 const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify(empty))); vi.stubGlobal("fetch", fetcher);
 render(<Demo />); fireEvent.click(screen.getByRole("button", { name: "Analyze synthetic example" }));
 expect(await screen.findByText("Synthetic headphones")).toBeTruthy();
 expect(screen.getByText(/Authored synthetic data/)).toBeTruthy();
 expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({ example: "patterns" });
 fireEvent.click(screen.getByRole("button", { name: "Reset demo" })); expect(screen.queryByText("Synthetic headphones")).toBeNull();
});
test("cancel prevents late response from replacing cleared results", async () => {
 let finish!: (v: Response) => void;
 vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(resolve => { finish = resolve; })));
 render(<Demo />); fireEvent.click(screen.getByRole("button", { name: "Analyze synthetic example" }));
 fireEvent.click(screen.getByRole("button", { name: "Cancel demo" }));
 await act(async () => finish(new Response(JSON.stringify(empty))));
 expect(screen.queryByText("Synthetic headphones")).toBeNull();
});
test("demo validator rejects live origin and numeric scores", () => {
 expect(isDemo(empty)).toBe(true); expect(isDemo({ ...empty, evidence_origin: "collected" })).toBe(false);
 expect(isDemo({ ...empty, analyzed_reviews: 1, analysis: { schema_version: "2", origin: "authored_fixture", review_count: 1, score: { value: 90 } } })).toBe(false);
});
