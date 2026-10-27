import type { NextConfig } from "next";

const config: NextConfig = {
  // Keep builds scoped to this app even when a parent directory has a lockfile.
  turbopack: { root: import.meta.dirname },
};

export default config;
