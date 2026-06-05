"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { 
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-gray-800 rounded-lg flex items-center justify-center text-xs text-gray-500">Initializing Chart Engine...</div> 
});

export default function ChartRenderer({ config, data }: { config: any, data: any[] }) {
    if (!config || !data || data.length === 0) return <div className="text-red-500 text-xs p-2 border border-red-900/30 rounded">Invalid Chart Specification</div>;

    const plotData = useMemo(() => {
        let trace: any = {
            type: config.chart_type,
            name: config.title || "Data"
        };
        
        if (config.chart_type === "pie") {
            trace.labels = data.map((row: any) => row[config.x_axis]);
            trace.values = data.map((row: any) => row[config.y_axis]);
            trace.marker = { 
                colors: ["#27272a", "#3f3f46", "#52525b", "#71717a", "#a1a1aa", "#d4d4d8", "#e4e4e7"] 
            };
            trace.textinfo = "percent";
            trace.hoverinfo = "label+percent+value";
        } else {
            trace.x = data.map((row: any) => row[config.x_axis]);
            trace.y = data.map((row: any) => row[config.y_axis]);
            trace.marker = { color: "#71717a", opacity: 0.8 }; // zinc-500
            
            if (config.chart_type === "scatter") {
                trace.mode = "markers";
                trace.marker = { size: 8, color: "#a1a1aa", opacity: 0.6 };
            }
            if (config.chart_type === "line") {
                trace.line = { color: "#e4e4e7", width: 2 }; // zinc-200
            }
        }
        
        return [trace];
    }, [config, data]);

    return (
        <div className="w-full h-80 glass-panel rounded-xl overflow-hidden my-4">
            <Plot
                data={plotData}
                layout={{
                    title: {
                        text: config.title || "Visualização",
                        font: { size: 14, color: "#a1a1aa", family: "Inter, sans-serif" }
                    },
                    autosize: true,
                    margin: { l: 40, r: 20, t: 40, b: 40 },
                    paper_bgcolor: "rgba(0,0,0,0)",
                    plot_bgcolor: "rgba(0,0,0,0)",
                    font: { color: "#71717a", family: "Inter, sans-serif", size: 11 },
                    hoverlabel: {
                        bgcolor: "#18181b", // zinc-900
                        bordercolor: "#27272a",
                        font: { color: "#e4e4e7", family: "Inter, sans-serif" }
                    },
                    xaxis: { 
                        title: { text: config.x_axis, font: { size: 10 } },
                        gridcolor: "rgba(255,255,255,0.02)", 
                        zerolinecolor: "rgba(255,255,255,0.05)",
                        showline: false
                    },
                    yaxis: { 
                        title: { text: config.y_axis, font: { size: 10 } },
                        gridcolor: "rgba(255,255,255,0.02)", 
                        zerolinecolor: "rgba(255,255,255,0.05)",
                        showline: false
                    }
                }}
                config={{ 
                    displayModeBar: false, 
                    responsive: true 
                }}
                useResizeHandler={true}
                className="w-full h-full animate-in fade-in slide-in-from-bottom-2 duration-700"
            />
        </div>
    );
}
