import type { Correction, Report, Status } from "./types";
import { isFake } from "./constants";

export const parseTs = (ts: string) => new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(ts) ? ts : ts + "Z").getTime();

export function ago(ts: string, now: number): string {
  const s = Math.max(0, Math.round((now - parseTs(ts)) / 1000));
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  return `${Math.round(s / 3600)} h ago`;
}

export const statusOf = (r: Report, corrections: Record<string, Correction>): Status =>
  isFake(r.verdict) && r.detail && corrections[r.detail] ? "corrected" : r.verdict;

// stable pseudo-random offset per report id
export function jitter(id: number, scale: number): [number, number] {
  const a = Math.sin(id * 12.9898) * 43758.5453;
  const b = Math.sin(id * 78.233) * 12543.123;
  return [(a - Math.floor(a) - 0.5) * scale, (b - Math.floor(b) - 0.5) * scale];
}

export const fmtInt = (n: number) => new Intl.NumberFormat("en-US").format(n);
