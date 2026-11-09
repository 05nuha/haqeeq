"use client";
import dynamic from "next/dynamic";

const UaeMap = dynamic(() => import("./UaeMap"), {
  ssr: false,
  loading: () => <div className="map-wrap"><div className="empty" style={{ paddingTop: "30%" }}>Loading map…</div></div>,
});
export default UaeMap;
