"use client";
import type { Correction, Report } from "@/lib/types";
import CountUp from "./CountUp";

export default function Kpis({ reports, corrections, demoMode }: { reports: Report[]; corrections: Record<string, Correction>; demoMode: boolean }) {
  const scoped = demoMode ? reports.filter((r) => !r.seeded) : reports;
  const n = (v: string) => scoped.filter((r) => r.verdict === v).length;
  const sub = demoMode ? "live forwards only" : "incl. simulated background";
  const cards = [
    { l: "Checks today", ar: "فحوصات اليوم", v: scoped.length, c: "var(--accent)" },
    { l: "Verified genuine", ar: "محتوى صحيح", v: n("genuine"), c: "var(--genuine)" },
    { l: "Altered official posts", ar: "منشورات معدّلة", v: n("altered"), c: "var(--altered)" },
    { l: "Scam messages", ar: "رسائل احتيال", v: n("scam_risk"), c: "var(--scam)" },
    { l: "Corrections sent", ar: "تصحيحات مرسلة", v: Object.keys(corrections).length, c: "var(--corrected)" },
  ];
  return (
    <section className="kpis">
      {cards.map((k) => (
        <div key={k.l} className="kpi" style={{ ["--c" as string]: k.c }}>
          <div className="l"><span>{k.l}</span><span className="ar" dir="rtl">{k.ar}</span></div>
          <div className="v"><CountUp value={k.v} /></div>
          <div className="s">{k.l === "Corrections sent" ? "operator-triggered" : sub}</div>
        </div>
      ))}
    </section>
  );
}
