import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  distDir: 'dist',
  reactStrictMode: true,
  typedRoutes: true,
  images: {
    unoptimized: true,
    formats: ["image/webp", "image/avif"],
    minimumCacheTTL: 60,
  },
  compress: true,
  turbopack: {
    root: ".",
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-DNS-Prefetch-Control",
            value: "on",
          },
        ],
      },
    ];
  },
  async redirects() {
    return [];
  },
  async rewrites() {
    return {
      beforeFiles: [],
    };
  },
};

export default nextConfig;
