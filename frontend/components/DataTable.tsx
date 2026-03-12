"use client";

import { useMemo } from "react";

export default function DataTable({ dataJson }: { dataJson: string }) {
    const data = useMemo(() => {
        try {
            const parsed = JSON.parse(dataJson);
            return parsed.results || [];
        } catch (e) {
            console.error("Invalid Table JSON", e);
            return [];
        }
    }, [dataJson]);

    if (!data || data.length === 0) return null;

    const columns = Object.keys(data[0]);

    return (
        <div className="w-full overflow-x-auto my-4 rounded-lg border border-[var(--color-glass-border)]">
            <table className="w-full text-left border-collapse bg-[rgba(255,255,255,0.02)]">
                <thead>
                    <tr className="border-b border-[var(--color-glass-border)] bg-[rgba(255,255,255,0.05)]">
                        {columns.map(col => (
                            <th key={col} className="p-3 text-xs font-bold uppercase tracking-wider text-[var(--color-neon-blue)]">
                                {col}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.slice(0, 10).map((row: any, idx: number) => (
                        <tr key={idx} className="border-b border-[var(--color-glass-border)] hover:bg-[rgba(255,255,255,0.05)] transition-colors">
                            {columns.map(col => (
                                <td key={col} className="p-3 text-sm text-gray-300">
                                    {typeof row[col] === 'number' ? row[col].toLocaleString() : String(row[col])}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
            {data.length > 10 && (
                <div className="p-2 text-[10px] text-center text-gray-500 italic">
                    Showing top 10 rows
                </div>
            )}
        </div>
    );
}
