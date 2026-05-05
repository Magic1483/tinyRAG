import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output:"export",
  devIndicators: false,
  allowedDevOrigins: ["*"]
};

export default nextConfig;
