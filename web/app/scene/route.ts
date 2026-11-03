export function GET() {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Interactive computer</title><style>html,body,spline-viewer{margin:0;width:100%;height:100%;display:block;background:#121614}</style></head><body><script type="module" src="https://cdn.spline.design/@splinetool/viewer@2.0.126/build/spline-viewer.js"></script><spline-viewer loading="eager" url="https://prod.spline.design/K5UevsEfu27gxzSe/scene.splinecode"></spline-viewer></body></html>`, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "Content-Security-Policy": `default-src 'none'; sandbox allow-scripts; script-src 'wasm-unsafe-eval' https://cdn.spline.design; style-src 'unsafe-inline'; connect-src blob: https://prod.spline.design https://cdn.spline.design https://unpkg.com/@splinetool/runtime@2.0.126/build/bevel.wasm https://www.gstatic.com/draco/versioned/decoders/1.5.2/ https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5WZLCzYlKw.ttf; img-src data: blob: https://prod.spline.design https://cdn.spline.design; media-src data: blob:; worker-src blob:; frame-ancestors 'self'; base-uri 'none'; form-action 'none'`,
      "X-Frame-Options": "SAMEORIGIN",
      "Referrer-Policy": "no-referrer",
      "X-Content-Type-Options": "nosniff",
      "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    },
  });
}



