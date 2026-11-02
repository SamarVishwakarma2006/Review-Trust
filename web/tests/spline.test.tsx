import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import SplineHero from "../app/spline-hero";
import { GET } from "../app/scene/route";

test("external scene is opt-in and removable with an opaque sandbox", () => {
  render(<SplineHero />);
  expect(screen.queryByTitle("Spline interactive computer")).toBeNull();
  fireEvent.click(screen.getByText("Explore in 3D"));
  expect(screen.getByTitle("Spline interactive computer").getAttribute("sandbox")).toBe("allow-scripts");
  fireEvent.click(screen.getByText("Stop animation"));
  expect(screen.queryByTitle("Spline interactive computer")).toBeNull();
  const policy = GET().headers.get("Content-Security-Policy")!;
  expect(policy).toContain("sandbox allow-scripts;");
  expect(policy).not.toContain("'unsafe-eval'");
  expect(policy).not.toContain("allow-same-origin");
});
