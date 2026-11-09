"use client";
import { useEffect, useState } from "react";
import { KIND_ICON, LABELS, PILL_ICON, imageUrl } from "@/lib/constants";
import type { Correction, Report } from "@/lib/types";
import { ago, statusOf } from "@/lib/utils";

export default function Feed({
  reports, corrections, selectedId, newIds, onSelect,
}: { reports: Report[]; corrections: Record<string, Correction>; selectedId: number | null; newIds: Set<number>; onSelect: (id: number) => void }) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const iv = setInterval(() => setNow(Date.now()), 5000);
    return () => clearInterval(iv);
  }, []);
  return (
    <div className="panel">
      <div className="ph"><span>Live citizen reports <span className="ar" dir="rtl">· بلاغات المواطنين</span></span><span>{reports.length}</span></div>
      <div className="pb">
        {!reports.length && <div className="empty">Waiting for forwarded messages…</div>}
        {reports.slice(0, 80).map((r) => {
          const st = statusOf(r, corrections);
          const img = imageUrl(r.image_path);
          return (
            <div key={r.id} className={`item ${r.id === selectedId ? "sel" : ""} ${newIds.has(r.id) ? "new" : ""}`} onClick={() => onSelect(r.id)}>
              {r.kind === "image" && img ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img className="thumb" src={img} alt="" loading="lazy" />
              ) : (
                <div className="thumb">{KIND_ICON[r.kind] ?? "📄"}</div>
              )}
              <div className="meta">
                <div className="top">
                  <span className="t">{LABELS[st].en} <span className="ar" dir="rtl" style={{ color: "#8193b2" }}>{LABELS[st].ar}</span></span>
                  <span className={`pill ${st}`}>{PILL_ICON[st]} {st.replace("_", " ")}</span>
                </div>
                <div className="sub">{r.detail ?? ""}</div>
                <div className="when">
                  <span>{r.emirate ?? "—"}</span>·<span>{ago(r.ts, now)}</span>·<span>{r.sender_masked ?? ""}</span>
                  {r.seeded && <span className="tag-sim">simulated</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
