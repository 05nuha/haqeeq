"use client";
import type { OpenDataset } from "@/lib/types";
import { fmtInt } from "@/lib/utils";

const badgeClass = (p: string) => (/bayanat/i.test(p) ? "bayanat" : /pulse/i.test(p) ? "dubai" : /fcsc/i.test(p) ? "fcsc" : "other");

export default function OpenData({ datasets, entitiesCount }: { datasets: OpenDataset[]; entitiesCount: number }) {
  return (
    <div className="panel">
      <div className="ph"><span>Open data <span className="ar" dir="rtl">· البيانات المفتوحة</span></span><span>{datasets.length} datasets</span></div>
      <div className="pb">
        {!datasets.length && <div className="empty">No datasets catalogued.</div>}
        {datasets.map((d) => (
          <a key={d.id} className="od" href={d.url} target="_blank" rel="noreferrer" style={{ color: "inherit", textDecoration: "none" }}>
            <span className={`badge ${badgeClass(d.portal)}`}>{d.portal}</span>
            <span className="nm" title={`${d.name} — ${d.publisher}`}>{d.name}</span>
            <span className="rw">{d.rows != null ? `${fmtInt(d.rows)} rows` : ""}</span>
            <span className="pw">{d.publisher} → <b style={{ color: "#536d70", fontWeight: 600 }}>{d.powers}</b></span>
          </a>
        ))}
        {entitiesCount > 0 && <div className="od-foot">Source check runs against <b style={{ color: "#e6edf8" }}>{fmtInt(entitiesCount)}</b> registered government entities.</div>}
      </div>
    </div>
  );
}
