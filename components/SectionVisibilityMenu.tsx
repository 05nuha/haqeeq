"use client";
import { useEffect, useRef, useState } from "react";

export const SECTION_NAMES = {
  kpis: "Monitoring summary",
  reports: "Live reports",
  sources: "Threat intelligence sources",
  flags: "Flagged activity",
  genuine: "Genuine activity · chart series",
  ranking: "Regional ranking",
  trending: "Misinformation trends",
} as const;

export type SectionKey = keyof typeof SECTION_NAMES;
export type SectionVisibility = Record<SectionKey, boolean>;

export default function SectionVisibilityMenu({
  visibility, onToggle,
}: { visibility: SectionVisibility; onToggle: (key: SectionKey, visible: boolean) => void }) {
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (event.target instanceof Node && !root.current?.contains(event.target)) setOpen(false);
    };
    const escape = (event: KeyboardEvent) => { if (event.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("mousedown", close); document.removeEventListener("keydown", escape); };
  }, []);

  const hidden = Object.values(visibility).filter((visible) => !visible).length;
  return (
    <div className="section-menu" ref={root}>
      <button className="section-menu-trigger" aria-expanded={open} aria-haspopup="true" onClick={() => setOpen((value) => !value)}>
        <span className="control-sliders" aria-hidden="true">☷</span> Sections{hidden > 0 && <span className="hidden-count">{hidden} hidden</span>}
      </button>
      {open && <div className="section-menu-popover" role="group" aria-label="Dashboard section visibility">
        <div className="section-menu-title">Visible sections</div>
        {(Object.entries(SECTION_NAMES) as [SectionKey, string][]).map(([key, label]) => (
          <label className="section-menu-row" key={key}>
            <input type="checkbox" checked={visibility[key]} onChange={(event) => onToggle(key, event.target.checked)} />
            <span>{label}</span>
            <small>{visibility[key] ? "Shown" : "Hidden"}</small>
          </label>
        ))}
        <div className="section-menu-fixed">Map and Forensic view are always visible.</div>
      </div>}
    </div>
  );
}
