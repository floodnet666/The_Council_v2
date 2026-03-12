"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function ChartRenderer({ spec }: { spec: string }) {
    const data = useMemo(() => {
        try {
            return JSON.parse(spec);
        } catch (e) {
            console.error("Invalid Chart JSON", e);
            return null;
        }
    }, [spec]);

    if (!data) return <div className="text-red-500 text-xs">Invalid Chart Data</div>;

    return (
        <div className="w-full h-64 glass-panel rounded-lg overflow-hidden">
            <Plot
                data={data.data}
                layout={{
                    ...data.layout,
                    width: undefined,
                    height: undefined,
                    autosize: true,
                    margin: { l: 40, r: 20, t: 40, b: 40 }
                }}
                useResizeHandler={true}
                style={{ width: "100%", height: "100%" }}
                config={{ displayModeBar: false }}
            />
        </div>
    );
}
