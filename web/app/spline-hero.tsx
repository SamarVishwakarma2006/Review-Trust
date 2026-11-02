"use client";
import { useState } from "react";
import Image from "next/image";

export default function SplineHero() {
  const [active, setActive] = useState(false);
  return <aside className="spline-hero" aria-label="Interactive computer illustration">
    <div className="spline-stage">
      <Image src="/spline-preview.png" alt="A smiling retro computer with green eyes, an orange lamp and a keyboard" fill sizes="(max-width: 640px) 100vw, 50vw" style={{ objectFit: "cover" }} priority />
      {active && <iframe src="/scene" title="Spline interactive computer" sandbox="allow-scripts" referrerPolicy="no-referrer" />}
    </div>
    <div className="spline-caption">
      <button onClick={() => setActive(!active)}>{active ? "Stop animation" : "Explore in 3D"}</button>
      <p>{active ? "Loading can take a moment. Stop animation to return to the image." : "Optional animation loads from Spline when you choose Explore in 3D."}</p>
      <a href="https://app.spline.design/community/file/63aa1f20-fbd1-4b3d-9a99-6a8a825917ca" target="_blank" rel="noopener noreferrer">Cute Computer Follow Cursor · original scene on Spline</a>
    </div>
  </aside>;
}
