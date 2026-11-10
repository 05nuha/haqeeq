"use client";
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from "chart.js";
import { useEffect, useMemo, useState } from "react";
import { Bar } from "react-chartjs-2";
import { isFake } from "@/lib/constants";
import type { Report } from "@/lib/types";
import { parseTs } from "@/lib/utils";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function ActivityChart({ reports }: { reports: Report[] }) {
  const [tick, setTick] = useState(() => Date.now());
  useEffect(() => {
    const iv = setInterval(() => setTick(Date.now()), 15000);
    return () => clearInterval(iv);
  }, []);
  const { labels, fakes, genuine } = useMemo(() => {
    const n = 12, size = 300000;
    const fakes = new Array(n).fill(0), genuine = new Array(n).fill(0);
    const labels = Array.from({ length: n }, (_, i) => (i === n - 1 ? "now" : `-${(n - 1 - i) * 5}m`));
    for (const r of reports) {
      const idx = n - 1 - Math.floor((tick - parseTs(r.ts)) / size);
      if (idx < 0 || idx >= n) continue;
      if (isFake(r.verdict)) fakes[idx]++; else genuine[idx]++;
    }
    return { labels, fakes, genuine };
  }, [reports, tick]);

  return (
    <div className="panel">
      <div className="ph"><span>Flagged vs genuine · last 60 min <span className="ar" dir="rtl">· النشاط</span></span><span>5-min buckets</span></div>
      <div className="chart-body">
        <Bar
          data={{ labels, datasets: [
            { label: "Flagged", data: fakes, backgroundColor: "rgba(184,77,72,.76)", borderRadius: 3, stack: "s" },
            { label: "Genuine", data: genuine, backgroundColor: "rgba(25,128,94,.7)", borderRadius: 3, stack: "s" },
          ] }}
          options={{
            responsive: true, maintainAspectRatio: false, animation: { duration: 400 },
            plugins: { legend: { position: "top", align: "end", labels: { color: "#627a7e", boxWidth: 8, boxHeight: 8, font: { size: 10 } } } },
            scales: {
              x: { stacked: true, ticks: { color: "#627a7e", font: { size: 9 } }, grid: { display: false } },
              y: { stacked: true, ticks: { color: "#627a7e", precision: 0, font: { size: 9 } }, grid: { color: "rgba(22,53,59,.08)" } },
            },
          }}
        />
      </div>
    </div>
  );
}
