/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV !== "production";

const nextConfig = {
  reactStrictMode: true,
  // Dev only: forward /api/* to the local Python dev server. In production Vercel serves api/*.py itself.
  async rewrites() {
    if (!isDev) return [];
    return [{ source: "/api/:path*", destination: "http://127.0.0.1:5328/api/:path*" }];
  },
};

export default nextConfig;
