"use client";
import { useState } from "react";
import Image from "next/image";

export default function SplineHero() {
  const [active, setActive] = useState(true);
  return <aside className="spline-hero" aria-label="Interactive computer illustration">
    <div className="spline-stage">
      <Image src="/review-desk.webp" alt="" fill sizes="100vw" style={{ objectFit: "cover" }} preload />
      {active && <iframe src="/scene" title="Spline interactive computer" sandbox="allow-scripts" referrerPolicy="no-referrer" />}
    </div>
    <div className="spline-caption">
      <button onClick={() => setActive(!active)}>{active ? "Pause 3D" : "Resume 3D"}</button>
    </div>
  </aside>;
}
