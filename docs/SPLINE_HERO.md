# Optional homepage illustration — 2026-11-02

Owner supplied scene K5UevsEfu27gxzSe and authorized integration. The homepage uses
a local still capture by default and an explicit Explore in 3D / Stop animation
control. No autoplay, including for reduced-motion users. Responsive square sizing
reserves space. Stop removes the frame and restores the still if loading fails.

Viewer 2.0.126 runs at /scene inside sandbox=allow-scripts, with no same-origin,
forms, popups or top-navigation permission. The route also applies CSP sandbox
allow-scripts for direct visits. Only this fixed decorative route bypasses the
ordinary nonce proxy and supplies its own CSP/security/no-store headers. Its CSP
allows WebAssembly compilation, not JavaScript eval; scripts come from Spline CDN,
connections from Spline and the exact pinned unpkg bevel.wasm path and versioned gstatic Draco decoder path. The parent
analyzer policy and input isolation are retained. No submitted data reaches the scene.

Original community file attribution is linked visibly; Spline badge retained.
Preview is a captured still, not a new original asset. Creator identity/additional
credit details should be confirmed from the original community file before launch.
Privacy text discloses optional external requests. No npm dependencies or deployment.

Frontend regression tests cover opt-in/removal and opaque sandbox policy. Existing
content test now allows the exact attribution URL while retaining local-link checks.

Verification: 36 frontend tests passed, ESLint/typecheck/production build passed.
Browser rendered the scene after allowing its pinned WebAssembly dependencies;
keyboard Enter starts/stops the frame and Tab reaches attribution. Confirmed a
320px viewport with document scroll width 305px (no horizontal overflow), inspected
the stacked still/control layout, and reset the viewport afterward. Scene remains
opt-in; no claim of broad mobile GPU/performance testing or provider retention audit.

## Approved visual redesign — 2026-11-03

The home hero now uses local AI-generated `web/public/review-desk.webp`, derived
from the approved concept, with real HTML headings/links over it. It is an artistic
interpretation, not a capture of the live Spline scene. The original opt-in scene
is below the analyzer in its own section. Its sandbox, CSP, stop control and
attribution are unchanged. No external asset request is needed for the hero.
