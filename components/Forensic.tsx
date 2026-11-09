"use client";
import { useEffect, useState } from "react";
import { COLORS, LABELS, imageUrl } from "@/lib/constants";
import type { Correction, OfficialPost, Report } from "@/lib/types";
import { ago, statusOf } from "@/lib/utils";

type StepKind = "ok" | "bad" | "warn" | "na";
interface Step { k: StepKind; t: string; d: React.ReactNode; badge?: React.ReactNode; note?: string }
const ICON: Record<StepKind, string> = { ok: "✓", bad: "✕", warn: "!", na: "–" };

function Heat({ heat }: { heat: number[][] }) {
  return (
    <div className="heat">
      {heat.flatMap((row, y) => row.map((v, x) => <i key={`${y}-${x}`} style={{ ["--a" as string]: Math.min(0.85, v * 0.9) }} />))}
    </div>
  );
}

export default function Forensic({
  report, corrections, officialPosts, entitiesCount,
}: { report: Report | null; corrections: Record<string, Correction>; officialPosts: Record<string, OfficialPost>; entitiesCount: number }) {
  const [now, setNow] = useState(() => Date.now());
  const [showHeat, setShowHeat] = useState(true);
  useEffect(() => {
    const iv = setInterval(() => setNow(Date.now()), 5000);
    return () => clearInterval(iv);
  }, []);
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setShowHeat(true);
  }, [report?.id]);

  if (!report) {
    return (
      <div className="panel">
        <div className="ph"><span>Forensic view <span className="ar" dir="rtl">· التحليل الجنائي</span></span></div>
        <div className="pb"><div className="empty">Select a report to see how the engine reached its verdict.</div></div>
      </div>
    );
  }

  const r = report;
  const st = statusOf(r, corrections);
  const official = r.matched_id ? officialPosts[r.matched_id] : undefined;
  const fwd = imageUrl(r.image_path);
  const off = imageUrl(official?.image_path);
  const sim = r.kind === "image" && r.distance != null ? Math.max(0, Math.round((1 - r.distance / 64) * 100)) : null;
  const n = entitiesCount > 0 ? entitiesCount.toLocaleString("en-US") : "the";
  const steps: Step[] = [];

  if (r.kind === "image") {
    steps.push({ k: "bad", t: "1 · Signature check (C2PA)", d: "C2PA signature not found — stripped by WhatsApp in transit.", note: "Signing key is a mocked government key (demo)." });
    if (r.matched_id) {
      steps.push({ k: "ok", t: "2 · Fingerprint match", d: <>Matches official post “{official?.title ?? r.matched_id}”{official ? ` (${official.issuer})` : ""} · distance <b>{r.distance}/64</b> · similarity <b>{sim}%</b></> });
      const pct = r.changed_pct != null ? `${r.changed_pct}%` : "";
      steps.push(r.verdict === "altered"
        ? { k: "bad", t: "3 · Tamper check", d: <>Edited region detected versus the official original — <b>{pct} of pixels changed</b>.</> }
        : { k: "ok", t: "3 · Tamper check", d: <>No edited regions — {pct ? `${pct} changed, ` : ""}identical content to the official original.</> });
    } else {
      steps.push({ k: "na", t: "2 · Fingerprint match", d: <>No match in the official registry (closest <b>{r.distance ?? "–"}/64</b>, similarity {sim ?? "–"}%).</> });
      steps.push({ k: "warn", t: "3 · Source check", d: `Not issued by any of the ${n} registered government entities. Unverified — not proof of a fake.` });
    }
  } else {
    steps.push({ k: "na", t: "1 · Source check", d: `Forwarded text — no match among ${n} registered government entities (Bayanat / Dubai Pulse).` });
    steps.push({
      k: r.verdict === "scam_risk" ? "bad" : "na",
      t: "2 · AI scam analysis",
      badge: r.ai_used ? <span className="ai-badge gem">✦ GEMINI</span> : <span className="ai-badge rules">RULES</span>,
      d: <>{r.detail}{r.ai_reason && <span className="ar" dir="rtl">{r.ai_reason}</span>}</>,
    });
  }
  if (corrections[r.detail ?? ""]) steps.push({ k: "ok", t: "Official correction sent", d: <span className="ar" dir="rtl" style={{ fontSize: ".72rem" }}>{corrections[r.detail ?? ""].message}</span> });

  return (
    <div className="panel">
      <div className="ph"><span>Forensic view <span className="ar" dir="rtl">· التحليل الجنائي</span></span><span>#{r.id}</span></div>
      <div className="pb" key={r.id}>
        <div className="vbanner" style={{ ["--vc" as string]: COLORS[st] }}>
          <div><b>{LABELS[st].en}</b><span className="ar" dir="rtl">{LABELS[st].ar}</span></div>
          <small>{r.emirate ?? ""}{r.area ? ` · ${r.area}` : ""}<br />{ago(r.ts, now)}{r.seeded ? " · simulated" : " · live forward"}</small>
        </div>
        <div className="steps">
          {steps.map((s, i) => (
            <div key={i} className="step" style={{ animationDelay: `${0.25 + i * 0.4}s` }}>
              <div className={`ic ${s.k}`}>{ICON[s.k]}</div>
              <div>
                <div className="t">{s.t}{s.badge}</div>
                <div className="d">{s.d}</div>
                {s.note && <div className="note">{s.note}</div>}
              </div>
            </div>
          ))}
        </div>
        {r.kind === "image" && (
          <>
            <div className="compare">
              <figure>
                <div className="imgbox">
                  {fwd ? /* eslint-disable-next-line @next/next/no-img-element */ <img src={fwd} alt="Forwarded" /> : <div className="none">Forwarded image</div>}
                  {r.heat && showHeat && <Heat heat={r.heat} />}
                  <div className="scan" />
                </div>
                <figcaption>Forwarded by citizen {r.heat && <button className="mini-toggle" onClick={() => setShowHeat((v) => !v)}>{showHeat ? "hide" : "show"} heat-map</button>}</figcaption>
              </figure>
              <figure>
                <div className="imgbox">
                  {off ? /* eslint-disable-next-line @next/next/no-img-element */ <img src={off} alt="Official" /> : <div className="none">No official original in registry</div>}
                </div>
                <figcaption>Official registry copy</figcaption>
              </figure>
            </div>
            {sim != null && (
              <>
                <div className="simrow"><span>Visual fingerprint similarity</span><b>{sim}%</b></div>
                <div className="simbar"><div style={{ width: `${sim}%` }} /></div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
