import type { Status, Verdict } from "./types";

export const REPORT_COLUMNS =
  "id,ts,sender_masked,kind,verdict,matched_id,distance,changed_pct,heat,emirate,area,detail,ai_reason,ai_used,image_path,seeded";

export const EMIRATE_COORDS: Record<string, [number, number]> = {
  Dubai: [25.2048, 55.2708],
  "Abu Dhabi": [24.4539, 54.3773],
  Sharjah: [25.3463, 55.4209],
  Ajman: [25.4052, 55.5136],
  "Umm Al Quwain": [25.5647, 55.5552],
  "Ras Al Khaimah": [25.8007, 55.9762],
  Fujairah: [25.1288, 56.3265],
  "Al Ain": [24.2075, 55.7447],
};

// Where each emirate label sits relative to its hotspot (keeps the Dubai/Sharjah/Ajman/UAQ cluster readable).
export const LABEL_POS: Record<string, string> = {
  Dubai: "left",
  Sharjah: "bottom",
  Ajman: "right",
  "Umm Al Quwain": "top",
  "Ras Al Khaimah": "right",
  Fujairah: "right",
  "Abu Dhabi": "bottom",
  "Al Ain": "bottom",
};

export const EMIRATES_AR: Record<string, string> = {
  Dubai: "دبي",
  "Abu Dhabi": "أبوظبي",
  Sharjah: "الشارقة",
  Ajman: "عجمان",
  "Umm Al Quwain": "أم القيوين",
  "Ras Al Khaimah": "رأس الخيمة",
  Fujairah: "الفجيرة",
  "Al Ain": "العين",
};

export const COLORS: Record<Status, string> = {
  genuine: "#19805e",
  altered: "#b84d48",
  scam_risk: "#9a6b16",
  unverified: "#5f7075",
  corrected: "#167d70",
};

export const LABELS: Record<Status, { en: string; ar: string }> = {
  genuine: { en: "Verified genuine", ar: "صحيح" },
  altered: { en: "Altered official post", ar: "معدّل" },
  scam_risk: { en: "Scam risk", ar: "احتيال محتمل" },
  unverified: { en: "Unverified", ar: "غير مؤكد" },
  corrected: { en: "Corrected", ar: "تم التصحيح" },
};

export const PILL_ICON: Record<Status, string> = {
  genuine: "✅",
  altered: "🔴",
  scam_risk: "🔴",
  unverified: "⚪",
  corrected: "✓",
};

export const KIND_ICON: Record<string, string> = { image: "🖼️", text: "💬", link: "🔗" };

export const isFake = (v: Verdict) => v !== "genuine";

export const foldEmirate = (e: string | null) => (e === "Al Ain" ? "Abu Dhabi" : e);

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
export const SUPABASE_ANON = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";
export const SUPABASE_CONFIGURED = Boolean(SUPABASE_URL && SUPABASE_ANON);

export function imageUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("data:")) return path;
  return `${SUPABASE_URL}/storage/v1/object/public/media/${path}`;
}
