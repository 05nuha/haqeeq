"use client";
import Image from "next/image";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useDashboardData } from "@/lib/useDashboardData";
import ActivityChart from "./ActivityChart";
import Feed from "./Feed";
import Forensic from "./Forensic";
import Header from "./Header";
import Kpis from "./Kpis";
import MapLoader from "./MapLoader";
import OpenData from "./OpenData";
import Ranking from "./Ranking";
import Trending from "./Trending";
import SectionVisibilityMenu, { type SectionKey, type SectionVisibility } from "./SectionVisibilityMenu";

const TOKEN_KEY = "haqeeq_admin_token";
const SECTION_KEY = "haqeeq_dashboard_sections";
const DEFAULT_SECTIONS: SectionVisibility = { kpis: true, reports: true, sources: true, flags: true, genuine: true, ranking: true, trending: true };
const safeGet = (k: string) => { try { return localStorage.getItem(k) ?? ""; } catch { return ""; } };
const safeSet = (k: string, v: string) => { try { if (v) localStorage.setItem(k, v); else localStorage.removeItem(k); } catch { /* ignore */ } };

export default function Dashboard() {
  const { mode, data, newIds, latest, errorMsg, pushCorrection } = useDashboardData();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [focus, setFocus] = useState<{ emirate: string | null; nonce: number } | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [sectionVisibility, setSectionVisibility] = useState<SectionVisibility>(DEFAULT_SECTIONS);
  const [visibilityLoaded, setVisibilityLoaded] = useState(false);
  const [token, setToken] = useState("");
  const [modal, setModal] = useState<null | { pending?: string }>(null);
  const [draft, setDraft] = useState("");
  const [toast, setToast] = useState<{ html: React.ReactNode; err?: boolean } | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const userPinnedAt = useRef(0);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setToken(safeGet(TOKEN_KEY));
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        const saved = safeGet(SECTION_KEY);
        if (saved) {
          const parsed = JSON.parse(saved) as Partial<SectionVisibility>;
          const restored = { ...DEFAULT_SECTIONS };
          (Object.keys(restored) as SectionKey[]).forEach((key) => { restored[key] = parsed[key] !== false; });
          setSectionVisibility(restored);
        }
      } catch { /* Ignore invalid saved view preferences. */ }
      setVisibilityLoaded(true);
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (visibilityLoaded) safeSet(SECTION_KEY, JSON.stringify(sectionVisibility));
  }, [sectionVisibility, visibilityLoaded]);

  const showToast = useCallback((html: React.ReactNode, err = false) => {
    setToast({ html, err });
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 5200);
  }, []);

  // auto-open the newest report (map only zooms on user click); pause for 15 s after a manual pick
  useEffect(() => {
    if (!latest) return;
    if (Date.now() - userPinnedAt.current < 15000) return;
    setSelectedId(latest.id);
  }, [latest]);
  const firstId = data.reports[0]?.id ?? null;
  const effectiveSelected = selectedId ?? firstId;
  const selected = useMemo(() => data.reports.find((r) => r.id === effectiveSelected) ?? null, [data.reports, effectiveSelected]);

  const onSelect = useCallback((id: number) => {
    userPinnedAt.current = Date.now();
    setSelectedId(id);
    const r = data.reports.find((x) => x.id === id);
    if (r?.emirate) setFocus({ emirate: r.emirate, nonce: Date.now() });
  }, [data.reports]);

  const toggleSection = useCallback((key: SectionKey, visible: boolean) => {
    setSectionVisibility((current) => ({ ...current, [key]: visible }));
  }, []);

  const doPush = useCallback(async (detail: string, tok: string) => {
    const res = await pushCorrection(detail, tok);
    if (res.ok) {
      showToast(<><b>Correction sent</b> to {res.recipients ?? 0} citizens · {res.delivered ?? 0} delivered on WhatsApp<br /><span className="ar" dir="rtl" style={{ color: "#12645b" }}>تم إرسال التصحيح الرسمي</span></>);
    } else {
      if (res.status === 401) { safeSet(TOKEN_KEY, ""); setToken(""); }
      showToast(<><b>Could not send correction</b><br />{res.error}</>, true);
    }
  }, [pushCorrection, showToast]);

  const onPush = useCallback(async (detail: string) => {
    if (mode !== "mock" && !token) { setDraft(""); setModal({ pending: detail }); return; }
    await doPush(detail, token);
  }, [mode, token, doPush]);

  const saveToken = async () => {
    const t = draft.trim();
    if (!t) return;
    safeSet(TOKEN_KEY, t);
    setToken(t);
    const pending = modal?.pending;
    setModal(null);
    if (pending) await doPush(pending, t);
  };

  if (mode === "loading") return <div className="center-card"><div className="empty">Loading…</div></div>;
  if (mode === "unconfigured" || mode === "error") {
    return (
      <div className="center-card">
        <div className="card">
          <Image className="brand-logo" src="/logo.png" alt="Haqeeq shield and check mark" width={44} height={44} priority />
          <h2>{mode === "error" ? "Could not load dashboard data" : "Dashboard not configured"}</h2>
          {mode === "error" ? (
            <p>Supabase returned an error: <code>{errorMsg}</code>. Check the project URL, anon key, and that migration <code>0001_init.sql</code> has been applied.</p>
          ) : (
            <p>Set <code>NEXT_PUBLIC_SUPABASE_URL</code> and <code>NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in <code>.env.local</code> (or the Vercel project settings), then reload. The anon key is read-only.</p>
          )}
          <p>No backend handy? Preview the dashboard with simulated data.</p>
          <a className="btn go" href="?mock=1" style={{ textDecoration: "none" }}>Open demo with mock data →</a>
        </div>
      </div>
    );
  }

  const { reports, corrections, officialPosts, population, openDatasets, entitiesCount } = data;
  const showLeft = sectionVisibility.reports || sectionVisibility.sources;
  const showActivity = sectionVisibility.flags || sectionVisibility.genuine;
  const columns = [showLeft ? "minmax(18rem, 21.5rem)" : null, "minmax(0, 1fr)", "minmax(20rem, 26rem)"].filter(Boolean).join(" ");
  return (
    <div className="app" style={{ gridTemplateRows: sectionVisibility.kpis ? "auto auto auto minmax(0, 1fr) auto" : "auto auto minmax(0, 1fr) auto" }}>
      <Header mode={mode} demoMode={demoMode} onDemo={() => setDemoMode((v) => !v)} unlocked={Boolean(token)}
        onOperator={() => { if (token) { safeSet(TOKEN_KEY, ""); setToken(""); showToast(<><b>Operator locked</b></>); } else { setDraft(""); setModal({}); } }} />
      <div className="dashboard-tools"><span className="system-context">Panel visibility</span><SectionVisibilityMenu visibility={sectionVisibility} onToggle={toggleSection} /></div>
      {sectionVisibility.kpis && <section className="kpi-section" aria-label="Monitoring summary"><div className="section-heading">Monitoring summary</div><Kpis reports={reports} corrections={corrections} demoMode={demoMode} /></section>}
      <main className="main" style={{ gridTemplateColumns: columns }}>
        {showLeft && <div className="col col-left">
          {sectionVisibility.reports && <Feed reports={reports} corrections={corrections} selectedId={effectiveSelected} newIds={newIds} onSelect={onSelect} />}
          {sectionVisibility.sources && <OpenData datasets={openDatasets} entitiesCount={entitiesCount} />}
        </div>}
        <div className="col col-center" style={{ gridTemplateRows: showActivity || sectionVisibility.ranking ? "minmax(0, 1fr) 14.2rem" : "minmax(0, 1fr)" }}>
          <MapLoader reports={reports} corrections={corrections} population={population} latest={latest} focus={focus} onSelect={onSelect} />
          {(showActivity || sectionVisibility.ranking) && <div className={`bottom-row ${!showActivity || !sectionVisibility.ranking ? "single" : ""}`}>
            {showActivity && <ActivityChart reports={reports} flagsVisible={sectionVisibility.flags} genuineVisible={sectionVisibility.genuine} />}
            {sectionVisibility.ranking && <Ranking reports={reports} population={population} />}
          </div>}
        </div>
        <div className="col col-right">
          <Forensic report={selected} corrections={corrections} officialPosts={officialPosts} entitiesCount={entitiesCount} onPush={onPush} />
          {sectionVisibility.trending && <Trending reports={reports} corrections={corrections} onPush={onPush} />}
        </div>
      </main>
      <footer className="foot">
        <span><b>Simulated background</b><span className="dotsep">·</span><b>live forwards real</b><span className="dotsep">·</span><b>signing key mocked</b></span>
        <span>Approximate report origins · simulated routes · “Unverified” is not “proven fake”</span>
      </footer>
      {modal && (
        <div className="modal-bg" onClick={() => setModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Operator unlock <span className="ar" dir="rtl" style={{ color: "#38bdf8", fontSize: ".95rem" }}>· وصول المشغّل</span></h3>
            <p>Enter the dashboard admin token to push official corrections to citizens. It is kept in this browser only.</p>
            <input type="password" autoFocus placeholder="Admin token" value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => e.key === "Enter" && saveToken()} />
            <div className="row">
              <button className="btn ghost" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn" onClick={saveToken}>{modal.pending ? "Unlock & send" : "Unlock"}</button>
            </div>
          </div>
        </div>
      )}
      <div className={`toast ${toast ? "show" : ""} ${toast?.err ? "err" : ""}`}>{toast?.html}</div>
    </div>
  );
}
