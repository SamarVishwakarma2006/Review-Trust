import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import Home from "../app/page";

afterEach(cleanup);

test("foundation page identifies the product and clearly withholds analysis", () => {
  render(<Home />);

  expect(screen.getByRole("heading", { name: "ReviewTrust", level: 1 })).toBeTruthy();
  expect(screen.getByRole("region", { name: "In development" })).toBeTruthy();
  expect(screen.getByText(/Review submission and analysis are not available yet/)).toBeTruthy();
  expect(screen.getByText(/not proven deception/)).toBeTruthy();
  expect(screen.queryByRole("textbox")).toBeNull();
});
