"use client";
import { useEffect, useRef, useState } from "react";
import Image from "next/image";

export default function SplineHero() {
  const [active, setActive] = useState(true);
  const [visible, setVisible] = useState(false);
  const stage = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let inView = typeof IntersectionObserver === "undefined";
    const sync = () => setVisible(inView && document.visibilityState !== "hidden");
    const observer = inView ? null : new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting && entry.intersectionRatio > 0;
      sync();
    });
    if (stage.current) observer?.observe(stage.current);
    document.addEventListener("visibilitychange", sync);
    sync();
    return () => {
      observer?.disconnect();
      document.removeEventListener("visibilitychange", sync);
    };
  }, []);

  return <aside className="spline-hero" aria-label="Interactive computer illustration">
    <div className="spline-stage" ref={stage}>
      <Image src="/review-desk.webp" alt="" fill sizes="100vw" style={{ objectFit: "cover" }} preload />
      {active && visible && <iframe src="/scene" title="Spline interactive computer" sandbox="allow-scripts" referrerPolicy="no-referrer" />}
    </div>
    <div className="spline-caption">
      <button onClick={() => setActive(!active)}>{active ? "Pause 3D" : "Resume 3D"}</button>
    </div>
  </aside>;
}
