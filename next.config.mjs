/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV !== "production";

const nextConfig = {
  reactStrictMode: true,
  // Fallback: allow plain SUPABASE_URL / SUPABASE_ANON_KEY in Vercel (the anon key is public by design).
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL || "",
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || "",
  },
  // Dev only: forward /api/* to the local Python dev server. In production Vercel serves api/*.py itself.
  async rewrites() {
    if (!isDev) return [];
    return [{ source: "/api/:path*", destination: "http://127.0.0.1:5328/api/:path*" }];
  },
};

export default nextConfig;
