import type { Metadata } from "next";
export const dynamic = "force-dynamic";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReviewTrust | Experimental review analysis",
  description: "Evidence-based analysis of patterns in electronics reviews. Currently in development.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#content">Skip to content</a>
        <header className="site-header">
          <div className="site-shell site-topbar">
            <Link className="brand" href="/">ReviewTrust<span>Review patterns, explained</span></Link>
            <nav aria-label="Primary navigation">
              <Link href="/#analyze">Analyzer</Link>
              <Link href="/how-it-works">How it works</Link>
              <Link href="/methodology">Methodology</Link>
              <Link href="/privacy">Privacy</Link>
              <Link href="/contact">Contact</Link>
              <Link className="nav-demo" href="/#demo">Explore demo ↗</Link>
            </nav>
          </div>
        </header>
        {children}
        <footer className="site-footer">
          <div className="site-shell">
            <p><strong>ReviewTrust</strong> · Electronics · English · Experimental</p>
            <p>Patterns need context. No result verifies authenticity or product quality.</p>
            <nav aria-label="Footer navigation">
              <Link href="/methodology">Methodology and limitations</Link>
              <Link href="/privacy">Privacy policy</Link>
              <Link href="/contact">Questions and disputes</Link>
            </nav>
            <p className="muted">Development preview. Security and deployment reviews are pending.</p>
            <p className="muted">3D illustration: <a className="text-link" href="https://app.spline.design/community/file/63aa1f20-fbd1-4b3d-9a99-6a8a825917ca" target="_blank" rel="noopener noreferrer">Cute Computer Follow Cursor · original scene on Spline</a>. Loads automatically on the homepage; use Pause 3D to stop.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
