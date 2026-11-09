"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { REPORT_COLUMNS, SUPABASE_CONFIGURED } from "./constants";
import { createMockEngine, type MockEngine } from "./mock";
import { getSupabase } from "./supabase";
import type { Correction, DashboardData, OfficialPost, Report } from "./types";

export type Mode = "loading" | "unconfigured" | "live" | "mock" | "error";

const EMPTY: DashboardData = {
  reports: [],
  corrections: {},
  officialPosts: {},
  population: [],
  openDatasets: [],
  entitiesCount: 0,
};

export interface CorrectionResult {
  ok: boolean;
  recipients?: number;
  delivered?: number;
  status?: number;
  error?: string;
}

export interface LatestEvent {
  id: number;
  emirate: string | null;
  nonce: number;
}

export function useDashboardData() {
  const [mode, setMode] = useState<Mode>("loading");
  const [data, setData] = useState<DashboardData>(EMPTY);
  const [newIds, setNewIds] = useState<Set<number>>(new Set());
  const [latest, setLatest] = useState<LatestEvent | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const mockRef = useRef<MockEngine | null>(null);
  const seen = useRef<Set<number>>(new Set());
  const nonce = useRef(0);
  const first = useRef(true);

  const announce = useCallback((r: Report) => {
    nonce.current += 1;
    setLatest({ id: r.id, emirate: r.emirate, nonce: nonce.current });
    setNewIds((prev) => new Set(prev).add(r.id));
    setTimeout(() => setNewIds((prev) => {
      const n = new Set(prev);
      n.delete(r.id);
      return n;
    }), 2500);
  }, []);

  const addReport = useCallback((r: Report) => {
    if (seen.current.has(r.id)) return;
    seen.current.add(r.id);
    setData((d) => ({ ...d, reports: [r, ...d.reports].slice(0, 1500) }));
    announce(r);
  }, [announce]);

  // ---------- initial load + effects ----------
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const wantMock = params.get("mock") === "1";
    let cleanup: (() => void) | undefined;
    let cancelled = false;

    if (wantMock) {
      const engine = createMockEngine();
      mockRef.current = engine;
      const init = engine.initial();
      init.reports.forEach((r) => seen.current.add(r.id));
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setData(init);
      setMode("mock");
      const iv = setInterval(() => addReport(engine.next()), 6000);
      const kick = setTimeout(() => addReport(engine.next()), 1800);
      cleanup = () => {
        clearInterval(iv);
        clearTimeout(kick);
      };
      return () => cleanup?.();
    }

    const sb = getSupabase();
    if (!SUPABASE_CONFIGURED || !sb) {
      setMode("unconfigured");
      return;
    }

    async function fetchAll(initial: boolean) {
      if (!sb) return;
      try {
        const since = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
        const [rep, cor, posts, pop, ods, ent] = await Promise.all([
          sb.from("reports").select(REPORT_COLUMNS).gte("ts", since).order("ts", { ascending: false }).limit(1500),
          sb.from("corrections").select("detail,ts,message,recipients,delivered"),
          sb.from("official_posts").select("id,title,title_ar,issuer,date,image_path"),
          sb.from("population").select("emirate,population,older_share,year,source"),
          sb.from("open_datasets").select("id,name,publisher,portal,url,accessed,powers,rows"),
          sb.from("entities").select("id", { count: "exact", head: true }),
        ]);
        if (cancelled) return;
        const firstErr = [rep, cor, posts, pop, ods].find((x) => x.error)?.error;
        if (firstErr) throw new Error(firstErr.message);
        const reports = (rep.data ?? []) as unknown as Report[];
        const fresh = reports.filter((r) => !seen.current.has(r.id));
        reports.forEach((r) => seen.current.add(r.id));
        setData({
          reports,
          corrections: Object.fromEntries(((cor.data ?? []) as Correction[]).map((c) => [c.detail, c])),
          officialPosts: Object.fromEntries(((posts.data ?? []) as OfficialPost[]).map((p) => [p.id, p])),
          population: pop.data ?? [],
          openDatasets: ods.data ?? [],
          entitiesCount: ent.count ?? 0,
        });
        if (!initial && fresh.length) announce(fresh[0]);
        setMode("live");
        setErrorMsg("");
        first.current = false;
      } catch (e) {
        if (cancelled) return;
        setErrorMsg(e instanceof Error ? e.message : String(e));
        if (first.current) setMode("error");
      }
    }

    fetchAll(true);

    const channel = sb
      .channel("haqeeq-live")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "reports" }, async (payload) => {
        const id = (payload.new as { id?: number }).id;
        if (id == null || seen.current.has(id)) return;
        // re-select with explicit columns (never trust/need sender_id)
        const { data: row } = await sb.from("reports").select(REPORT_COLUMNS).eq("id", id).maybeSingle();
        if (row) addReport(row as unknown as Report);
      })
      .on("postgres_changes", { event: "*", schema: "public", table: "corrections" }, (payload) => {
        const row = payload.new as Correction | undefined;
        if (!row || !row.detail) return;
        setData((d) => ({ ...d, corrections: { ...d.corrections, [row.detail]: row } }));
      })
      .subscribe();

    const safety = setInterval(() => fetchAll(false), 30_000);
    return () => {
      cancelled = true;
      clearInterval(safety);
      sb.removeChannel(channel);
    };
  }, [addReport, announce]);

  const pushCorrection = useCallback(
    async (detail: string, token: string): Promise<CorrectionResult> => {
      const message = "توضيح رسمي: هذا المحتوى غير صحيح ولم يصدر عن أي جهة رسمية. يرجى عدم إعادة إرساله.";
      if (mode === "mock") {
        const matching = data.reports.filter((r) => r.detail === detail);
        const live = matching.filter((r) => !r.seeded).length;
        const c: Correction = { detail, ts: new Date().toISOString(), message, recipients: matching.length, delivered: live };
        await new Promise((res) => setTimeout(res, 600));
        setData((d) => ({ ...d, corrections: { ...d.corrections, [detail]: c } }));
        return { ok: true, recipients: c.recipients, delivered: c.delivered };
      }
      try {
        const res = await fetch("/api/correct", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Admin-Token": token },
          body: JSON.stringify({ detail, message }),
        });
        if (!res.ok) return { ok: false, status: res.status, error: res.status === 401 ? "Invalid operator token" : `Server error ${res.status}` };
        const j = (await res.json()) as { recipients?: number; delivered?: number };
        const c: Correction = { detail, ts: new Date().toISOString(), message, recipients: j.recipients ?? 0, delivered: j.delivered ?? 0 };
        setData((d) => ({ ...d, corrections: { ...d.corrections, [detail]: c } }));
        return { ok: true, recipients: j.recipients ?? 0, delivered: j.delivered ?? 0 };
      } catch (e) {
        return { ok: false, error: e instanceof Error ? e.message : "Network error" };
      }
    },
    [mode, data.reports],
  );

  return { mode, data, newIds, latest, errorMsg, pushCorrection };
}
