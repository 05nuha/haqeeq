import type { Correction, Population, Report } from "./types";
import { foldEmirate, isFake } from "./constants";

export interface SpotStat {
  name: string;
  total: number;
  fakes: number;
  open: number;
  worst: "altered" | "unverified" | null;
}

/** Per hotspot location (Al Ain kept as its own marker). */
export function spotStats(reports: Report[], corrections: Record<string, Correction>): Record<string, SpotStat> {
  const out: Record<string, SpotStat> = {};
  for (const r of reports) {
    if (!r.emirate) continue;
    const s = (out[r.emirate] ??= { name: r.emirate, total: 0, fakes: 0, open: 0, worst: null });
    s.total++;
    if (!isFake(r.verdict)) continue;
    s.fakes++;
    if (r.detail && corrections[r.detail]) continue;
    s.open++;
    if (r.verdict === "altered" || r.verdict === "scam_risk") s.worst = "altered";
    else if (!s.worst) s.worst = "unverified";
  }
  return out;
}

export interface RankRow {
  emirate: string;
  fakes: number;
  population: number | null;
  per100k: number | null;
  olderShare: number | null;
}

/** Fakes (all non-genuine reports) per emirate, Al Ain folded into Abu Dhabi, normalised per 100,000 residents. */
export function rankEmirates(reports: Report[], population: Population[]): RankRow[] {
  const counts: Record<string, number> = {};
  for (const r of reports) {
    const e = foldEmirate(r.emirate);
    if (!e || !isFake(r.verdict)) continue;
    counts[e] = (counts[e] ?? 0) + 1;
  }
  const popBy = Object.fromEntries(population.map((p) => [p.emirate, p]));
  const names = new Set([...Object.keys(counts), ...population.map((p) => p.emirate)]);
  const rows: RankRow[] = [...names].map((emirate) => {
    const p = popBy[emirate];
    const fakes = counts[emirate] ?? 0;
    return {
      emirate,
      fakes,
      population: p?.population ?? null,
      per100k: p?.population ? (fakes / p.population) * 100_000 : null,
      olderShare: p?.older_share ?? null,
    };
  });
  return rows.sort((a, b) => (b.per100k ?? -1) - (a.per100k ?? -1) || b.fakes - a.fakes);
}
