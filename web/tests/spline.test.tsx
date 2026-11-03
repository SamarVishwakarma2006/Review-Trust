import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import SplineHero from "../app/spline-hero";
import { GET } from "../app/scene/route";

test("hero scene starts automatically and can be paused with isolation retained", () => {
  render(<SplineHero />);
  expect(screen.getByTitle("Spline interactive computer").getAttribute("sandbox")).toBe("allow-scripts");
  fireEvent.click(screen.getByText("Pause 3D"));
  expect(screen.queryByTitle("Spline interactive computer")).toBeNull();
  fireEvent.click(screen.getByText("Resume 3D"));
  expect(screen.getByTitle("Spline interactive computer")).toBeTruthy();
  const policy = GET().headers.get("Content-Security-Policy")!;
  expect(policy).toContain("sandbox allow-scripts;");
  expect(policy).toContain("connect-src blob:");
  expect(policy).toContain("media-src data: blob:;");
  expect(policy).not.toContain("'unsafe-eval'");
  expect(policy).not.toContain("allow-same-origin");
});
