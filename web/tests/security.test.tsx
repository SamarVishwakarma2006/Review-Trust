import { NextRequest } from "next/server";
import { afterEach, expect, test, vi } from "vitest";
import { proxy } from "../proxy";
import { isResult } from "../lib/api";
import fixture from "./fixtures/analysis.json";

afterEach(() => vi.unstubAllEnvs());

test("production CSP replaces supplied policy with fresh script nonces and exact API origin", () => {
  vi.stubEnv("NODE_ENV", "production");
  vi.stubEnv("NEXT_PUBLIC_API_URL", "https://api.example.invalid");
  const request = new NextRequest("http://localhost/", { headers: { "Content-Security-Policy": "script-src * 'unsafe-inline'", "x-nonce": "attacker" } });
  const a = proxy(request), b = proxy(request);
  const csp = a.headers.get("Content-Security-Policy")!;
  const scripts = csp.split(";").find(s => s.trim().startsWith("script-src"))!;
  expect(scripts).toMatch(/'nonce-[A-Za-z0-9+/=]+'/);
  expect(scripts).toContain("'strict-dynamic'");
  expect(scripts).not.toMatch(/unsafe-inline|unsafe-eval|attacker/);
  expect(b.headers.get("Content-Security-Policy")).not.toEqual(csp);
  expect(csp).toContain("connect-src 'self' https://api.example.invalid;");
  expect(csp).toContain("frame-ancestors 'none'");
  expect(a.headers.get("x-middleware-request-content-security-policy")).toEqual(csp);
  expect(a.headers.get("Cache-Control")).toBe("no-store");
  expect(a.headers.get("X-Content-Type-Options")).toBe("nosniff");
  expect(a.headers.get("Referrer-Policy")).toBe("no-referrer");
});

test("public consumer rejects numeric scores, old methodology and missing withholding policy", () => {
  expect(isResult(fixture)).toBe(true);
  for (const value of [0, 100]) expect(isResult({ ...fixture, score: { ...fixture.score, value } })).toBe(false);
  expect(isResult({ ...fixture, methodology_version: "rt-patterns-0.2.0-experimental" })).toBe(false);
  expect(isResult({ ...fixture, score: { ...fixture.score, reason_codes: [] } })).toBe(false);
});
