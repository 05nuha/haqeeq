"use client";
import { useMemo } from "react";
import { EMIRATES_AR } from "@/lib/constants";
import { rankEmirates } from "@/lib/stats";
import type { Population, Report } from "@/lib/types";

export default function Ranking({ reports, population }: { reports: Report[]; population: Population[] }) {
  const rows = useMemo(() => rankEmirates(reports, population), [reports, population]);
  const max = Math.max(0.0001, ...rows.map((r) => r.per100k ?? 0));
  const hasOlder = rows.some((r) => r.olderShare != null);
  const src = population[0]?.source;
  return (
    <div className="panel">
      <div className="ph"><span>Verify Before You Share · campaign targeting</span><span className="ar" dir="rtl">أين نستهدف الحملة</span></div>
      <div className="rank-head">Reports needing verification per 100,000 residents <span style={{ color: "#627a7e" }}>· indicative; includes demo rows and unverified reports</span></div>
      <div className="pb" style={{ paddingTop: 0 }}>
        {!rows.length && <div className="empty">No population data.</div>}
        {rows.map((r, i) => (
          <div key={r.emirate} style={hasOlder ? { gridTemplateColumns: "1.1rem 9.6rem 1fr 4.2rem 3.2rem 4rem" } : undefined} className={`rank-row ${i === 0 && (r.per100k ?? 0) > 0 ? "first" : ""}`}>
            <span className="n">{i + 1}</span>
            <span className="e">{r.emirate}<small className="ar" dir="rtl">{EMIRATES_AR[r.emirate]}</small></span>
            <span className="bar"><div style={{ width: `${((r.per100k ?? 0) / max) * 100}%` }} /></span>
            <span className="v">{r.per100k != null ? r.per100k.toFixed(1) : "–"}<small> /100k</small></span>
            <span className="c">{r.fakes} reports</span>
            {hasOlder && <span className="c" title="Share of residents aged 60+">60+ {r.olderShare != null ? `${(r.olderShare * 100).toFixed(1)}%` : "–"}
            </span>}
          </div>
        ))}
        {src && <div className="od-foot">Population: {src}. Al Ain is counted within Abu Dhabi.</div>}
      </div>
    </div>
  );
}
