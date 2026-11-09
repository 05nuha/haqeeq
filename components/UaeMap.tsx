"use client";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useMemo, useState } from "react";
import { CircleMarker, MapContainer, Marker, TileLayer, Tooltip, useMap } from "react-leaflet";
import { COLORS, EMIRATE_COORDS, EMIRATES_AR, LABELS, LABEL_POS, foldEmirate, isFake } from "@/lib/constants";
import { rankEmirates, spotStats } from "@/lib/stats";
import type { Correction, Population, Report } from "@/lib/types";
import type { LatestEvent } from "@/lib/useDashboardData";
import { jitter, statusOf } from "@/lib/utils";

type TileSet = "carto" | "esri";
// CARTO dark_all is the intended basemap. Some networks get a placeholder "API KEY REQUIRED" tile back, so
// we probe one known tile and fall back to Esri's free dark-grey canvas. Override with ?tiles=carto|esri
// or NEXT_PUBLIC_MAP_TILES.
async function pickTiles(): Promise<TileSet> {
  const forced = new URLSearchParams(window.location.search).get("tiles") ?? process.env.NEXT_PUBLIC_MAP_TILES;
  if (forced === "carto" || forced === "esri") return forced;
  try {
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), 4000);
    const res = await fetch("https://a.basemaps.cartocdn.com/dark_all/8/179/108.png", { signal: ctrl.signal });
    clearTimeout(to);
    const blob = await res.blob();
    return res.ok && blob.size > 4000 ? "carto" : "esri";
  } catch {
    return "carto"; // CORS/network opaque: assume fine
  }
}

const BOUNDS: L.LatLngBoundsExpression = [[23.95, 54.0], [26.02, 56.5]];

function Controller({ focus, resetNonce }: { focus: { emirate: string | null; nonce: number } | null; resetNonce: number }) {
  const map = useMap();
  useEffect(() => {
    const c = focus?.emirate ? EMIRATE_COORDS[focus.emirate] : null;
    if (c) map.flyTo(c, 9, { duration: 0.8 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus?.nonce]);
  useEffect(() => {
    if (resetNonce > 0) map.flyToBounds(BOUNDS, { duration: 0.8 });
  }, [resetNonce, map]);
  useEffect(() => {
    const el = map.getContainer();
    const ro = new ResizeObserver(() => { map.invalidateSize(); });
    ro.observe(el);
    return () => ro.disconnect();
  }, [map]);
  return null;
}

function hotspotIcon(name: string, size: number, color: string, label: string, done: boolean) {
  const pos = LABEL_POS[name] ?? "";
  return L.divIcon({
    className: "",
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    html: `<div class="hotspot ${done ? "done" : ""}" style="--hc:${color};width:${size}px;height:${size}px">
      <div class="ring" style="width:${size}px;height:${size}px"></div><div class="ring r2" style="width:${size}px;height:${size}px"></div>
      <div class="core" style="width:${size * 0.6}px;height:${size * 0.6}px">${label}</div>
      <div class="nm ${pos}">${name}</div></div>`,
  });
}
const rippleIcon = L.divIcon({ className: "", iconSize: [20, 20], iconAnchor: [10, 10], html: '<div class="ripple"></div>' });

export default function UaeMap({
  reports, corrections, population, latest, focus, onSelect,
}: {
  reports: Report[]; corrections: Record<string, Correction>; population: Population[]; latest: LatestEvent | null;
  focus: { emirate: string | null; nonce: number } | null; onSelect: (id: number) => void;
}) {
  const [ripples, setRipples] = useState<{ key: number; pos: [number, number] }[]>([]);
  const [resetNonce, setResetNonce] = useState(0);
  const [tiles, setTiles] = useState<TileSet | null>(null);
  useEffect(() => {
    let alive = true;
    pickTiles().then((t) => alive && setTiles(t));
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    if (!latest?.emirate) return;
    const c = EMIRATE_COORDS[latest.emirate];
    if (!c) return;
    const [dy, dx] = jitter(latest.id, 0.16);
    const key = latest.nonce;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setRipples((r) => [...r, { key, pos: [c[0] + dy, c[1] + dx] }]);
    const t = setTimeout(() => setRipples((r) => r.filter((x) => x.key !== key)), 1600);
    return () => clearTimeout(t);
  }, [latest]);

  const spots = useMemo(() => spotStats(reports, corrections), [reports, corrections]);
  const rank = useMemo(() => Object.fromEntries(rankEmirates(reports, population).map((r) => [r.emirate, r])), [reports, population]);

  const dots = useMemo(
    () =>
      reports.flatMap((r) => {
        const c = r.emirate ? EMIRATE_COORDS[r.emirate] : null;
        if (!c) return [];
        const [dy, dx] = jitter(r.id, 0.16);
        return [{ r, pos: [c[0] + dy, c[1] + dx] as [number, number], st: statusOf(r, corrections) }];
      }),
    [reports, corrections],
  );

  return (
    <div className="map-wrap">
      <MapContainer bounds={BOUNDS} boundsOptions={{ padding: [10, 10] }} zoomControl={false} zoomSnap={0.1} minZoom={6.5} maxZoom={12}
        maxBounds={[[22.3, 51.0], [26.8, 57.2]]} style={{ position: "absolute", inset: 0 }}>
        {tiles === "carto" && (
          <TileLayer key="carto" url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" subdomains="abcd" maxZoom={19}
            attribution="&copy; OpenStreetMap &copy; CARTO" />
        )}
        {tiles === "esri" && (
          <>
            <TileLayer key="esri" url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
              maxZoom={16} attribution="Tiles &copy; Esri &mdash; Esri, DeLorme, HERE" />
          </>
        )}
        <Controller focus={focus} resetNonce={resetNonce} />
        {dots.map(({ r, pos, st }) => (
          <CircleMarker key={r.id} center={pos} radius={r.id === latest?.id ? 6 : 3.6} pathOptions={{ weight: 0, fillOpacity: 0.85, fillColor: COLORS[st] }}
            eventHandlers={{ click: () => onSelect(r.id) }}>
            <Tooltip className="hq-tip" direction="top"><b>{LABELS[st].en}</b><br /><span className="m">{r.emirate} · click to inspect</span></Tooltip>
          </CircleMarker>
        ))}
        {Object.values(spots).filter((s) => s.fakes > 0 && EMIRATE_COORDS[s.name]).map((s) => {
          const done = s.open === 0;
          const color = done ? COLORS.corrected : s.worst === "altered" ? COLORS.altered : COLORS.unverified;
          const size = Math.min(66, 26 + (done ? 1 : s.open) * 2.2);
          const folded = foldEmirate(s.name) as string;
          const rk = rank[folded];
          return (
            <Marker key={s.name} position={EMIRATE_COORDS[s.name]} icon={hotspotIcon(s.name, size, color, done ? "✓" : String(s.open), done)} zIndexOffset={s.name === "Sharjah" ? 1000 : s.open}>
              <Tooltip className="hq-tip" direction="top" offset={[0, -size / 2]}>
                <b>{s.name}</b> <span className="m ar" dir="rtl">{EMIRATES_AR[s.name]}</span><br />
                <span className="big">{s.fakes}</span> <span className="m">fake reports · {s.open} still open</span><br />
                {rk?.per100k != null ? (
                  <><b>{rk.per100k.toFixed(2)}</b> <span className="m">fake reports per 100,000 residents</span>
                    {s.name === "Al Ain" && <><br /><span className="m">(Al Ain counted within Abu Dhabi emirate)</span></>}
                    {s.name === "Abu Dhabi" && <><br /><span className="m">(emirate total incl. Al Ain: {rk.fakes})</span></>}</>
                ) : <span className="m">population data unavailable</span>}
              </Tooltip>
            </Marker>
          );
        })}
        {ripples.map((rp) => <Marker key={`rp${rp.key}`} position={rp.pos} icon={rippleIcon} interactive={false} zIndexOffset={2000} />)}
      </MapContainer>
      <div className="map-title">
        <b>Where fakes are being reported <span className="ar" dir="rtl">· أين تُرصد المحتويات المزيفة</span></b>
        <div>{reports.filter((r) => isFake(r.verdict)).length} fake reports · hotspot size = open (uncorrected) fakes</div>
      </div>
      <div className="map-caption">Map shows where reports come from — not the private WhatsApp spread path. (WhatsApp is end-to-end encrypted.)</div>
      <div className="legend">
        <span><i style={{ background: COLORS.altered }} />Altered / scam</span>
        <span><i style={{ background: COLORS.unverified }} />Unverified</span>
        <span><i style={{ background: COLORS.genuine }} />Genuine</span>
        <span><i style={{ background: COLORS.corrected }} />Corrected ✓</span>
      </div>
      <button className="chip reset-btn" onClick={() => setResetNonce((n) => n + 1)}>⤢ Reset view</button>
    </div>
  );
}
