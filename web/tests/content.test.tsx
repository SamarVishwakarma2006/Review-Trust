import { cleanup, render, screen } from "@testing-library/react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import RootLayout, { metadata } from "../app/layout";
import Home from "../app/page";
import HowItWorks from "../app/how-it-works/page";
import Methodology from "../app/methodology/page";
import Privacy from "../app/privacy/page";
import Contact from "../app/contact/page";

const contact = vi.hoisted(() => ({ email: "" }));
vi.mock("../lib/contact", () => ({ get CONTACT_EMAIL() { return contact.email; } }));
beforeEach(() => { contact.email = ""; });
afterEach(cleanup);

const pages = { "/": Home, "/how-it-works": HowItWorks, "/methodology": Methodology, "/privacy": Privacy, "/contact": Contact };

test("all public pages have one main/heading, focusable skip target and resolvable internal links", () => {
  for (const Page of Object.values(pages)) {
    const doc = new DOMParser().parseFromString(renderToStaticMarkup(<RootLayout><Page /></RootLayout>), "text/html");
    expect(doc.querySelectorAll("main")).toHaveLength(1);
    expect(doc.querySelectorAll("h1")).toHaveLength(1);
    expect(doc.querySelector("main#content")?.getAttribute("tabindex")).toBe("-1");
    expect(doc.querySelector(".skip-link")?.getAttribute("href")).toBe("#content");
    expect(doc.querySelector('nav[aria-label="Primary navigation"]')).toBeTruthy();
    expect(doc.querySelector('nav[aria-label="Footer navigation"]')).toBeTruthy();
    for (const anchor of doc.querySelectorAll<HTMLAnchorElement>("a[href]")) {
      const url = new URL(anchor.getAttribute("href")!, "http://localhost/");
      expect(url.origin).toBe("http://localhost");
      const Target = pages[url.pathname as keyof typeof pages];
      expect(Target).toBeTruthy();
      if (url.hash) {
        const targetDoc = new DOMParser().parseFromString(renderToStaticMarkup(<Target />), "text/html");
        expect(targetDoc.getElementById(url.hash.slice(1))).toBeTruthy();
      }
    }
  }
  expect(metadata.robots).toEqual({ index: false, follow: false });
});

test("contact is visibly unavailable when blank, with no broken email link or message form", () => {
  render(<Contact />);
  expect(screen.getByLabelText("No contact address configured")).toBeTruthy();
  expect(screen.getByText(/Questions and disputes cannot be sent/)).toBeTruthy();
  expect(document.querySelector('a[href^="mailto:"]')).toBeNull();
  expect(document.querySelector("form")).toBeNull();
  expect(screen.getByText(/Do not send original review files/)).toBeTruthy();
});

test("adding an owner email creates only an explicit mail link; privacy follows its configured state", () => {
  contact.email = "  questions+test@example.invalid  ";
  render(<Contact />);
  expect(screen.getByRole("link", { name: "questions+test@example.invalid" }).getAttribute("href"))
    .toBe("mailto:questions%2Btest%40example.invalid?subject=ReviewTrust%20question%20or%20dispute");
  expect(screen.getByText(/does not send a message automatically/)).toBeTruthy();
  cleanup(); render(<Privacy />);
  expect(screen.getByText(/A contact email link is available there/)).toBeTruthy();
  expect(screen.queryByText(/No address has been supplied/)).toBeNull();
});

test("privacy explains original CSV bytes, incomplete masking, memory limits and unverified hosting", () => {
  render(<Privacy />);
  expect(screen.getByText(/including unmapped columns/)).toBeTruthy();
  expect(screen.getByText(/raw upload bytes reach the API first/)).toBeTruthy();
  expect(screen.getByText(/not secure-erasure guarantees/)).toBeTruthy();
  expect(screen.getByText(/cannot promise that hosting infrastructure records nothing/)).toBeTruthy();
  expect(screen.getByText(/Contact and dispute submission remain unavailable/)).toBeTruthy();
});

test("methodology keeps literal-mention failure modes, context-only checks and release withholding explicit", () => {
  render(<Methodology />);
  expect(screen.getByText(/Quoted and negated phrases still count/)).toBeTruthy();
  expect(screen.getByText(/None of these three checks changes the index/)).toBeTruthy();
  expect(screen.getByText(/Precision, recall, F1/)).toBeTruthy();
  expect(screen.getByText(/Public numeric scores are not approved/)).toBeTruthy();
  expect(screen.getByText(/Both API routes now withhold numeric scores/)).toBeTruthy();
});
