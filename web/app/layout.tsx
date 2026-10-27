import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReviewTrust | Experimental review analysis",
  description: "Evidence-based analysis of patterns in electronics reviews. Currently in development.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
