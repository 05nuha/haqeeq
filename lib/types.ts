export type Verdict = "genuine" | "altered" | "unverified" | "scam_risk";
export type Status = Verdict | "corrected";

export interface Report {
  id: number;
  ts: string;
  sender_masked: string | null;
  kind: "image" | "text" | "link";
  verdict: Verdict;
  matched_id: string | null;
  distance: number | null;
  changed_pct: number | null;
  heat: number[][] | null;
  emirate: string | null;
  area: string | null;
  detail: string | null;
  ai_reason: string | null;
  ai_used: boolean | null;
  image_path: string | null;
  seeded: boolean;
}

export interface Correction {
  detail: string;
  ts: string;
  message: string;
  recipients: number;
  delivered: number;
}

export interface OfficialPost {
  id: string;
  title: string;
  title_ar: string | null;
  issuer: string;
  date: string | null;
  image_path: string;
}

export interface Population {
  emirate: string;
  population: number;
  older_share: number | null;
  year: number | null;
  source: string;
}

export interface OpenDataset {
  id: string;
  name: string;
  publisher: string;
  portal: string;
  url: string;
  accessed: string | null;
  powers: string;
  rows: number | null;
}

export interface DashboardData {
  reports: Report[];
  corrections: Record<string, Correction>;
  officialPosts: Record<string, OfficialPost>;
  population: Population[];
  openDatasets: OpenDataset[];
  entitiesCount: number;
}
