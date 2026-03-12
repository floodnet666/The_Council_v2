"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { 
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-gray-800 rounded-lg flex items-center justify-center text-xs text-gray-500">Initializing Chart Engine...</div> 
});

export default function ChartRenderer({ spec }: { spec: string }) {
    const chartData = useMemo(() => {
        try {
            return JSON.parse(spec);
        } catch (e) {
            console.error("Chart JSON parsing error:", e);
            return null;
        }
    }, [spec]);

    if (!chartData) return <div className="text-red-500 text-xs p-2 border border-red-900/30 rounded">Invalid Chart Specification</div>;

    return (
        <div className="w-full h-80 glass-panel rounded-xl overflow-hidden my-4 border border-cyan-900/30 shadow-2xl">
            <Plot
                data={chartData.data}
                layout={{
                    ...chartData.layout,
                    autosize: true,
                    margin: { l: 50, r: 30, t: 50, b: 50 },
                    paper_bgcolor: "rgba(0,0,0,0)",
                    plot_bgcolor: "rgba(0,0,0,0)",
                    font: { color: "#ededed", family: "Inter, sans-serif" },
                    xaxis: { gridcolor: "rgba(255,255,255,0.05)", zerolinecolor: "rgba(255,255,255,0.1)" },
                    yaxis: { gridcolor: "rgba(255,255,255,0.05)", zerolinecolor: "rgba(255,255,255,0.1)" }
                }}
                config={{ 
                    displayModeBar: false, 
                    responsive: true 
                }}
                useResizeHandler={true}
                className="w-full h-full"
            />
        </div>
    );
}
