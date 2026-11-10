"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import type { Mode } from "@/lib/useDashboardData";

export default function Header({
  mode, demoMode, onDemo, unlocked, onOperator,
}: { mode: Mode; demoMode: boolean; onDemo: () => void; unlocked: boolean; onOperator: () => void }) {
  const [clock, setClock] = useState("--:--:--");
  useEffect(() => {
    const f = () => setClock(new Date().toLocaleTimeString("en-GB", { timeZone: "Asia/Dubai" }));
    f();
    const iv = setInterval(f, 1000);
    return () => clearInterval(iv);
  }, []);
  return (
    <header className="hdr">
      <div className="brand">
        <Image className="brand-logo" src="/logo.svg" alt="Haqeeq mark" width={34} height={34} priority />
        <div>
          <h1>HAQEEQ</h1>
          <p>Content integrity monitoring</p>
        </div>
      </div>
      <div className="hdr-right">
        <button className={`chip ${demoMode ? "on" : ""}`} onClick={onDemo} title="ON: KPIs count live forwards only. OFF: KPIs include simulated background activity.">
          <span className="sw" /> {demoMode ? "Live only" : "Include simulated"}
        </button>
        <button className={`chip ${unlocked ? "unlocked" : ""}`} onClick={onOperator}>
          {unlocked ? "Operator access active" : "Operator access"}
        </button>
        <div className={`live ${mode === "mock" ? "mock" : ""}`}><i />{mode === "mock" ? "MOCK DATA" : "LIVE"}</div>
        <div className="clock">{clock}<small>GST · Dubai</small></div>
      </div>
    </header>
  );
}
