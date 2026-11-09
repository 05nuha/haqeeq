"use client";
import { useMemo, useState } from "react";
import { isFake } from "@/lib/constants";
import type { Correction, Report } from "@/lib/types";

export default function Trending({
  reports, corrections, onPush,
}: { reports: Report[]; corrections: Record<string, Correction>; onPush: (detail: string) => Promise<void> }) {
  const [busy, setBusy] = useState<string | null>(null);
  const list = useMemo(() => {
    const groups: Record<string, { n: number; places: Record<string, number> }> = {};
    for (const r of reports) {
      if (!isFake(r.verdict) || !r.detail) continue;
      const g = (groups[r.detail] ??= { n: 0, places: {} });
      g.n++;
      if (r.emirate) g.places[r.emirate] = (g.places[r.emirate] ?? 0) + 1;
    }
    return Object.entries(groups).sort((a, b) => b[1].n - a[1].n).slice(0, 8);
  }, [reports]);
  const max = list[0]?.[1].n ?? 1;

  return (
    <div className="panel">
      <div className="ph"><span>Trending fakes <span className="ar" dir="rtl">· الأكثر انتشاراً</span></span><span>Act now</span></div>
      <div className="pb">
        {!list.length && <div className="empty">No fakes trending.</div>}
        {list.map(([detail, g]) => {
          const done = Boolean(corrections[detail]);
          const where = Object.entries(g.places).sort((a, b) => b[1] - a[1]).slice(0, 3).map((p) => p[0]).join(", ");
          return (
            <div key={detail} className={`trend ${done ? "done" : ""}`}>
              <div className="r1"><span className="nm">{detail}</span><span className="cnt">{g.n}</span></div>
              <div className="bar"><div style={{ width: `${(g.n / max) * 100}%` }} /></div>
              <div className="wh">
                <span>{done ? `Corrected · ${corrections[detail].recipients} citizens notified` : `Reported in ${where}`}</span>
                <button className={`btn ${done ? "done" : ""}`} disabled={done || busy === detail}
                  onClick={async () => { setBusy(detail); await onPush(detail); setBusy(null); }}>
                  {done ? "✓ Correction sent" : busy === detail ? "Sending…" : "Push official correction"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
