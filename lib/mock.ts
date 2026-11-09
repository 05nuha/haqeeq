// Client-side MOCK data for ?mock=1 — realistic, fictional, uses the canonical scenarios from CONTRACT section 5.
import type { DashboardData, OfficialPost, OpenDataset, Population, Report, Verdict } from "./types";

const D = {
  explosions: "Fake: 'explosions in Downtown Dubai' image",
  holiday: "Altered: public holiday notice with a fake date",
  police: "Scam: 'Dubai Police fine — pay now via link'",
  burj: "Fake: AI video of Burj Khalifa collapsing",
  eid: "Scam: 'Emirates ID suspended — verify OTP'",
  mohre: "Matches official MOHRE announcement",
  weekend: "Matches official weekend schedule notice",
};

interface Scenario {
  kind: "image" | "text";
  verdict: Verdict;
  detail: string;
  weight: number;
  matched?: string;
}
const SCENARIOS: Scenario[] = [
  { kind: "image", verdict: "unverified", detail: D.explosions, weight: 14 },
  { kind: "image", verdict: "altered", detail: D.holiday, weight: 8, matched: "public_holiday_notice" },
  { kind: "text", verdict: "scam_risk", detail: D.police, weight: 7 },
  { kind: "image", verdict: "unverified", detail: D.burj, weight: 6 },
  { kind: "text", verdict: "scam_risk", detail: D.eid, weight: 4 },
  { kind: "image", verdict: "genuine", detail: D.mohre, weight: 6, matched: "mohre_working_hours" },
  { kind: "image", verdict: "genuine", detail: D.weekend, weight: 4, matched: "weekend_schedule_notice" },
];

const EMIRATE_WEIGHTS: [string, number][] = [
  ["Dubai", 8], ["Sharjah", 5], ["Abu Dhabi", 4], ["Ajman", 3], ["Al Ain", 2],
  ["Ras Al Khaimah", 2], ["Fujairah", 1], ["Umm Al Quwain", 1],
];

function pick<T>(items: [T, number][] | (T & { weight: number })[], rnd: () => number): T {
  const arr = (items as unknown[]).map((x) => (Array.isArray(x) ? x : [x, (x as { weight: number }).weight])) as [T, number][];
  const total = arr.reduce((s, x) => s + x[1], 0);
  let r = rnd() * total;
  for (const [v, w] of arr) {
    r -= w;
    if (r <= 0) return v;
  }
  return arr[0][0];
}

// ---------- fictional poster images (inline SVG data URIs) ----------
function poster(opts: { title: string; sub: string; issuer: string; date: string; accent: string; fake?: boolean }): string {
  const { title, sub, issuer, date, accent, fake } = opts;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101c3a"/><stop offset="1" stop-color="#0a1226"/></linearGradient>
  <radialGradient id="r" cx=".5" cy=".6" r=".6"><stop offset="0" stop-color="#ff7a2f" stop-opacity=".9"/><stop offset="1" stop-color="#ff7a2f" stop-opacity="0"/></radialGradient></defs>
  <rect width="640" height="480" fill="url(#g)"/>
  <rect x="14" y="14" width="612" height="452" rx="14" fill="none" stroke="${accent}" stroke-width="3"/>
  ${fake ? `<ellipse cx="330" cy="330" rx="260" ry="150" fill="url(#r)"/><polygon points="300,420 320,240 345,300 365,200 395,420" fill="#1b1b1b"/>` : `<circle cx="320" cy="120" r="38" fill="${accent}" opacity=".9"/><text x="320" y="135" text-anchor="middle" font-size="42" font-family="Arial" fill="#04111f" font-weight="700">★</text>`}
  <text x="320" y="${fake ? 70 : 200}" text-anchor="middle" font-size="30" font-family="Arial, sans-serif" fill="#fff" font-weight="700">${title}</text>
  <text x="320" y="${fake ? 110 : 245}" text-anchor="middle" font-size="19" font-family="Arial, sans-serif" fill="#b6c4e0">${sub}</text>
  <rect x="170" y="290" width="300" height="52" rx="10" fill="${accent}" opacity=".18"/>
  <text x="320" y="325" text-anchor="middle" font-size="26" font-family="Arial, sans-serif" fill="#fff" font-weight="700">${date}</text>
  <text x="320" y="420" text-anchor="middle" font-size="15" font-family="Arial, sans-serif" fill="#8fa3c8">${issuer}</text>
  <text x="320" y="446" text-anchor="middle" font-size="11" font-family="Arial, sans-serif" fill="#5d7196">FICTIONAL DEMO IMAGE</text>
  </svg>`;
  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

const IMG = {
  official_holiday: poster({ title: "Public holiday notice", sub: "Official announcement", issuer: "Federal Authority for Government HR", date: "Fri 2 Dec 2026", accent: "#2dd4bf" }),
  fake_holiday: poster({ title: "Public holiday notice", sub: "Official announcement", issuer: "Federal Authority for Government HR", date: "Mon 5 Dec 2026", accent: "#2dd4bf" }),
  mohre: poster({ title: "Working-hours announcement", sub: "Summer midday break update", issuer: "MOHRE", date: "15 Jun – 15 Sep", accent: "#38bdf8" }),
  weekend: poster({ title: "Weekend schedule notice", sub: "Government working week", issuer: "Government Media Office", date: "Sat – Sun", accent: "#a78bfa" }),
  explosions: poster({ title: "BREAKING: explosions", sub: "Downtown Dubai", issuer: "unknown source", date: "LIVE", accent: "#f97316", fake: true }),
  burj: poster({ title: "BREAKING: Burj collapses", sub: "AI-generated video frame", issuer: "unknown source", date: "VIRAL", accent: "#f97316", fake: true }),
};

const OFFICIAL: OfficialPost[] = [
  { id: "mohre_working_hours", title: "MOHRE announcement", title_ar: "إعلان وزارة الموارد البشرية والتوطين", issuer: "Ministry of Human Resources & Emiratisation (MOHRE)", date: "2026-06-15", image_path: IMG.mohre },
  { id: "weekend_schedule_notice", title: "Weekend schedule notice", title_ar: "إشعار جدول عطلة نهاية الأسبوع", issuer: "UAE Government Media Office", date: "2026-01-01", image_path: IMG.weekend },
  { id: "public_holiday_notice", title: "Public holiday notice", title_ar: "إعلان العطلة الرسمية", issuer: "Federal Authority for Government HR", date: "2026-12-02", image_path: IMG.official_holiday },
];

const POPULATION: Population[] = [
  { emirate: "Abu Dhabi", population: 3790000, older_share: 0.042, year: 2023, source: "FCSC (mock figures)" },
  { emirate: "Dubai", population: 3650000, older_share: 0.031, year: 2023, source: "FCSC (mock figures)" },
  { emirate: "Sharjah", population: 1800000, older_share: 0.038, year: 2023, source: "FCSC (mock figures)" },
  { emirate: "Ajman", population: 540000, older_share: 0.035, year: 2023, source: "FCSC (mock figures)" },
  { emirate: "Ras Al Khaimah", population: 410000, older_share: 0.052, year: 2023, source: "FCSC (mock figures)" },
  { emirate: "Fujairah", population: 260000, older_share: 0.057, year: 2023, source: "FCSC (mock figures)" },
  { emirate: "Umm Al Quwain", population: 85000, older_share: 0.049, year: 2023, source: "FCSC (mock figures)" },
];

const DATASETS: OpenDataset[] = [
  { id: "bayanat_entities", name: "Government entities directory", publisher: "UAE Federal Government", portal: "Bayanat", url: "https://bayanat.ae/en/entities", accessed: "2026-11-09", powers: "Trusted-source registry (source check)", rows: 142 },
  { id: "dp_org_register", name: "Organisation register", publisher: "Dubai Digital Authority", portal: "Dubai Pulse", url: "https://www.dubaipulse.gov.ae/registers/orgztoa", accessed: "2026-11-09", powers: "Trusted-source registry (Dubai entities)", rows: 88 },
  { id: "fcsc_population", name: "Population estimates by emirate", publisher: "Federal Competitiveness & Statistics Centre", portal: "FCSC Open Data", url: "https://opendata.fcsc.gov.ae", accessed: "2026-11-09", powers: "Per-100k risk ranking", rows: 7 },
  { id: "dp_population_community", name: "Population by community", publisher: "Dubai Statistics Center", portal: "Dubai Pulse", url: "https://www.dubaipulse.gov.ae/data/dsc-statistics/dsc_population_by_community-open", accessed: "2026-11-09", powers: "Dubai community-level map", rows: 226 },
  { id: "dp_areas", name: "DLD areas lookup", publisher: "Dubai Land Department", portal: "Dubai Pulse", url: "https://www.dubaipulse.gov.ae/data/dld-transactions/dld_lkp_areas-open", accessed: "2026-11-09", powers: "Dubai area names", rows: 330 },
];

const DUBAI_AREAS = ["Deira", "Business Bay", "Jumeirah", "Al Barsha", "Dubai Marina", "Al Quoz"];
const AR_SCAM_POLICE = "الرسالة تنتحل صفة شرطة دبي وتطلب دفع غرامة عبر رابط خارجي مع ضغط زمني — مؤشرات احتيال واضحة.";
const AR_SCAM_EID = "الرسالة تدّعي تعليق الهوية الإماراتية وتطلب رمز التحقق (OTP) — لا تشارك الرمز مع أحد.";

export interface MockEngine {
  initial: () => DashboardData;
  next: () => Report;
}

export function createMockEngine(): MockEngine {
  let seed = 20261109;
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) % 4294967296;
    return seed / 4294967296;
  };
  let nextId = 1000;
  const phones = () => `+97150${Math.floor(rnd() * 9)}•••${String(Math.floor(rnd() * 900) + 100)}`;

  function heatFor(): number[][] {
    const g = Array.from({ length: 16 }, () => Array.from({ length: 16 }, () => 0));
    // edited date strip, rows 9-11, cols 4-11
    for (let y = 9; y <= 11; y++) for (let x = 4; x <= 11; x++) g[y][x] = Math.min(1, 0.55 + rnd() * 0.45);
    for (let y = 8; y <= 12; y++) for (let x = 3; x <= 12; x++) if (g[y][x] === 0) g[y][x] = rnd() * 0.25;
    return g;
  }

  function make(ageMs: number, live: boolean): Report {
    const s = pick<Scenario>(SCENARIOS as (Scenario & { weight: number })[], rnd);
    const emirate = pick<string>(EMIRATE_WEIGHTS, rnd);
    const id = nextId++;
    const r: Report = {
      id,
      ts: new Date(Date.now() - ageMs).toISOString(),
      sender_masked: phones(),
      kind: s.kind,
      verdict: s.verdict,
      matched_id: s.matched ?? null,
      distance: null,
      changed_pct: null,
      heat: null,
      emirate,
      area: emirate === "Dubai" ? DUBAI_AREAS[Math.floor(rnd() * DUBAI_AREAS.length)] : null,
      detail: s.detail,
      ai_reason: null,
      ai_used: null,
      image_path: null,
      seeded: !live,
    };
    if (s.kind === "image") {
      if (s.verdict === "genuine") {
        r.distance = Math.floor(rnd() * 4);
        r.changed_pct = Math.round(rnd() * 3) / 100;
        r.image_path = s.matched === "mohre_working_hours" ? IMG.mohre : IMG.weekend;
      } else if (s.verdict === "altered") {
        r.distance = 3 + Math.floor(rnd() * 5);
        r.changed_pct = Math.round((0.4 + rnd() * 0.9) * 100) / 100;
        r.heat = heatFor();
        r.image_path = IMG.fake_holiday;
        r.detail = s.detail;
      } else {
        r.distance = 24 + Math.floor(rnd() * 10);
        r.image_path = s.detail === D.burj ? IMG.burj : IMG.explosions;
      }
    } else {
      r.ai_used = live ? rnd() > 0.35 : rnd() > 0.5;
      r.ai_reason = r.ai_used ? (s.detail === D.police ? AR_SCAM_POLICE : AR_SCAM_EID) : null;
    }
    return r;
  }

  return {
    initial: () => {
      const reports: Report[] = [];
      for (let i = 0; i < 58; i++) reports.push(make((0.5 + rnd() * 57) * 60_000, false));
      reports.sort((a, b) => Date.parse(b.ts) - Date.parse(a.ts));
      return {
        reports,
        corrections: {},
        officialPosts: Object.fromEntries(OFFICIAL.map((p) => [p.id, p])),
        population: POPULATION,
        openDatasets: DATASETS,
        entitiesCount: 142 + 88,
      };
    },
    next: () => make(0, true),
  };
}
