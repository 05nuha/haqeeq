"use client";
import { useMemo, useState } from "react";
import { isFake } from "@/lib/constants";
import type { Correction, Report } from "@/lib/types";

export default function Trending({
  reports, corrections, onPush,
}: { reports: Report[]; corrections: Record<string, Correction>; onPush: (detail: string) => Promise<void> }) {
  const [busy, setBusy] = useState<string | null>(null);
  const list = useMemo(() => {
    const groups: Record<string, { n: number }> = {};
    for (const r of reports) {
      if (!isFake(r.verdict) || !r.detail) continue;
      const g = (groups[r.detail] ??= { n: 0 });
      g.n++;
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
          return (
            <div key={detail} className={`trend ${done ? "done" : ""}`}>
              <div className="r1"><span className="nm">{detail}</span><span className="cnt">{g.n}</span></div>
              <div className="bar"><div style={{ width: `${(g.n / max) * 100}%` }} /></div>
              {done ? (
                <div className="trend-success" role="status">Corrected · sent to {corrections[detail].recipients} citizens</div>
              ) : (
                <button className="btn trend-push" disabled={busy === detail}
                  onClick={async () => { setBusy(detail); try { await onPush(detail); } finally { setBusy(null); } }}>
                  {busy === detail ? "Sending…" : "Push official correction"}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
