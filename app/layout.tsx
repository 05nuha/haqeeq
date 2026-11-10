import type { Metadata, Viewport } from "next";
import { Inter, Noto_Kufi_Arabic } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const kufi = Noto_Kufi_Arabic({ subsets: ["arabic"], weight: ["600", "700"], variable: "--font-kufi", display: "swap" });

export const metadata: Metadata = {
  title: "HAQEEQ | Content Integrity",
  description: "Operational monitoring for content verification reports.",
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#0b141d" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${kufi.variable}`}>
      <body>{children}</body>
    </html>
  );
}
