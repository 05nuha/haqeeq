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

const TOKEN_KEY = "haqeeq_admin_token";
const safeGet = (k: string) => { try { return localStorage.getItem(k) ?? ""; } catch { return ""; } };
const safeSet = (k: string, v: string) => { try { v ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch { /* ignore */ } };

export default function Dashboard() {
  const { mode, data, newIds, latest, errorMsg, pushCorrection } = useDashboardData();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [focus, setFocus] = useState<{ emirate: string | null; nonce: number } | null>(null);
  const [demoMode, setDemoMode] = useState(false);
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

  const showToast = useCallback((html: React.ReactNode, err = false) => {
    setToast({ html, err });
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 5200);
  }, []);

  // auto-open the newest report (map only zooms on user click); pause for 15 s after a manual pick
  useEffect(() => {
    if (!latest) return;
    if (Date.now() - userPinnedAt.current < 15000) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
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
          <Image className="brand-logo" src="/logo.svg" alt="Haqeeq shield and check mark" width={44} height={44} priority />
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
  return (
    <div className="app">
      <Header mode={mode} demoMode={demoMode} onDemo={() => setDemoMode((v) => !v)} unlocked={Boolean(token)}
        onOperator={() => { if (token) { safeSet(TOKEN_KEY, ""); setToken(""); showToast(<><b>Operator locked</b></>); } else { setDraft(""); setModal({}); } }} />
      <Kpis reports={reports} corrections={corrections} demoMode={demoMode} />
      <main className="main">
        <div className="col col-left">
          <Feed reports={reports} corrections={corrections} selectedId={effectiveSelected} newIds={newIds} onSelect={onSelect} />
          <OpenData datasets={openDatasets} entitiesCount={entitiesCount} />
        </div>
        <div className="col col-center">
          <MapLoader reports={reports} corrections={corrections} population={population} latest={latest} focus={focus} onSelect={onSelect} />
          <div className="bottom-row">
            <ActivityChart reports={reports} />
            <Ranking reports={reports} population={population} />
          </div>
        </div>
        <div className="col col-right">
          <Forensic report={selected} corrections={corrections} officialPosts={officialPosts} entitiesCount={entitiesCount} />
          <Trending reports={reports} corrections={corrections} onPush={onPush} />
        </div>
      </main>
      <footer className="foot">
        <span><b>Background activity simulated</b><span className="dotsep">·</span><b>live forwards real</b><span className="dotsep">·</span><b>government signing key mocked</b></span>
        <span>Emirate of live reports is a demo pick · Map shows report origin, not WhatsApp spread · “Unverified” never means “proven fake”</span>
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
