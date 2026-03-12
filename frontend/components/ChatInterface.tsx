"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import ChartRenderer from "@/components/ChartRenderer";
import DataTable from "@/components/DataTable";

type Message = {
    role: "user" | "assistant";
    content: string;
    agent?: string;
};

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // File Upload State
    const [uploading, setUploading] = useState(false);
    const [currentFile, setCurrentFile] = useState<{ name: string, path: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;

        const file = e.target.files[0];
        
        // Validation: Only CSV and Parquet are supported by the DataEngine
        const validExtensions = ['.csv', '.parquet'];
        const fileName = file.name.toLowerCase();
        if (!validExtensions.some(ext => fileName.endsWith(ext))) {
            alert("Invalid file format. Please upload a .csv or .parquet file.");
            if (fileInputRef.current) fileInputRef.current.value = "";
            return;
        }

        setUploading(true);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/upload", { method: "POST", body: formData });
            if (!res.ok) throw new Error("Upload failed");
            
            const data = await res.json();
            if (data.status === "uploaded") {
                setCurrentFile({ name: data.filename, path: data.path });
                setMessages(prev => [
                    ...prev, 
                    { 
                        role: "assistant", 
                        content: `**File Detected**: \`${data.filename}\`\nI've indexed this datasource. What would you like to analyze?`,
                        agent: "system"
                    }
                ]);
            }
        } catch (err) {
            console.error(err);
            alert("Upload failed. Please ensure the backend is running.");
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            const res = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: userMsg.content,
                    file_path: currentFile?.path
                }),
            });

            if (!res.ok) throw new Error("Failed to fetch");

            const data = await res.json();
            const aiMsg: Message = {
                role: "assistant",
                content: data.response,
                agent: data.agent
            };
            setMessages((prev) => [...prev, aiMsg]);

        } catch (error) {
            console.error(error);
            const errorMsg: Message = { role: "assistant", content: "Error communicating with The Council." };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const renderContent = (msg: Message) => {
        const content = msg.content;

        // 1. Handle LIBRARIAN_RESPONSE
        if (content.includes("LIBRARIAN_RESPONSE:\n")) {
            const text = content.replace("LIBRARIAN_RESPONSE:\n", "");
            return (
                <div className="space-y-2">
                    <div className="flex items-center gap-2 text-[var(--color-neon-purple)] font-bold text-[10px] uppercase tracking-widest mb-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-neon-purple)] shadow-[0_0_5px_var(--color-neon-purple)]"></span>
                        Archive Search Result
                    </div>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{text}</p>
                </div>
            );
        }

        // 2. Handle CHART_JSON
        if (content.includes("CHART_JSON:")) {
            const marker = "CHART_JSON:";
            const splitPoint = content.indexOf(marker);
            const preText = content.substring(0, splitPoint).trim();
            const postMarker = content.substring(splitPoint + marker.length);

            const jsonMatch = postMarker.match(/^(\{.*?\})(\n\n|$)/s);
            if (jsonMatch) {
                const spec = jsonMatch[1];
                const remaining = postMarker.substring(jsonMatch[0].length).trim();

                return (
                    <div className="space-y-4 w-full min-w-[300px]">
                        {preText && <p className="text-sm leading-relaxed">{preText}</p>}
                        <ChartRenderer spec={spec} />
                        {remaining && <p className="text-sm border-l-2 border-[var(--color-neon-blue)] pl-3 text-gray-400 italic">{remaining}</p>}
                    </div>
                );
            }
        }

        // 3. Handle ANALYSIS_DATA
        if (content.includes("ANALYSIS_DATA:\n")) {
            const marker = "ANALYSIS_DATA:\n";
            const splitPoint = content.indexOf(marker);
            const preText = content.substring(0, splitPoint).trim();
            const postMarker = content.substring(splitPoint + marker.length);

            const jsonMatch = postMarker.match(/^(\{.*?\})(\n\n|$|---)/s);
            if (jsonMatch) {
                const dataJson = jsonMatch[1];
                const remaining = postMarker.substring(jsonMatch[0].length).replace(/^---\n/, "").trim();

                return (
                    <div className="space-y-4 w-full">
                        {preText && <p className="text-sm leading-relaxed">{preText}</p>}
                        <DataTable dataJson={dataJson} />
                        {remaining && (
                            <div className="pt-2 border-t border-[var(--color-glass-border)]">
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">{remaining}</p>
                            </div>
                        )}
                    </div>
                );
            }
        }

        return <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>;
    };

    return (
        <section className="flex-1 flex flex-col relative h-[calc(100vh-6rem)]">
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                className="hidden"
                accept=".csv,.parquet"
            />

            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-6 opacity-80">
                        <div className="h-24 w-24 rounded-full border border-[var(--color-glass-border)] flex items-center justify-center bg-[var(--color-surface)] glow-blue transition-all duration-500 hover:scale-105">
                            <span className="text-4xl">👁️</span>
                        </div>
                        <h2 className="text-2xl font-light">How can The Council assist you today?</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
                            <button onClick={() => fileInputRef.current?.click()} className="glass-panel p-4 rounded-xl text-left hover:bg-[var(--color-surface-hover)] transition-all hover:border-[var(--color-neon-blue)] group cursor-pointer">
                                <div className="text-sm font-semibold text-[var(--color-neon-blue)] mb-1 group-hover:glow-blue">Analyze Data</div>
                                <div className="text-xs text-gray-400">Upload a CSV and get instant insights.</div>
                            </button>
                            <button onClick={() => setInput("Generate a report")} className="glass-panel p-4 rounded-xl text-left hover:bg-[var(--color-surface-hover)] transition-all hover:border-[var(--color-neon-purple)] group cursor-pointer">
                                <div className="text-sm font-semibold text-[var(--color-neon-purple)] mb-1 group-hover:glow-purple">Generate Report</div>
                                <div className="text-xs text-gray-400">Create a comprehensive PDF report.</div>
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col gap-6 max-w-4xl mx-auto pb-24 w-full">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} w-full`}>
                                <div className={`
                                    max-w-[90%] md:max-w-[80%] p-4 rounded-2xl glass-panel relative w-fit
                                    ${msg.role === "user" ? "border-l-0 bg-[rgba(255,255,255,0.02)]" : "border-[var(--color-neon-blue)] border-opacity-30"}
                                `}>
                                    {msg.agent && (
                                        <div className="absolute -top-3 left-4 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[var(--color-surface)] border border-[var(--color-glass-border)] text-[var(--color-neon-blue)]">
                                            {msg.agent}
                                        </div>
                                    )}
                                    {renderContent(msg)}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="max-w-[80%] p-4 rounded-2xl glass-panel flex items-center gap-2">
                                    <div className="w-2 h-2 bg-[var(--color-neon-blue)] rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-[var(--color-neon-blue)] rounded-full animate-bounce delay-75"></div>
                                    <div className="w-2 h-2 bg-[var(--color-neon-blue)] rounded-full animate-bounce delay-150"></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            <div className="p-4 md:p-6 pb-8 glass-panel border-x-0 border-b-0 absolute bottom-0 w-full bg-[var(--background)]/80 backdrop-blur-md">
                <div className="max-w-4xl mx-auto relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                        placeholder="Ask The Council..."
                        className="w-full bg-[var(--color-surface)] border border-[var(--color-glass-border)] rounded-full py-4 pl-12 pr-12 text-white placeholder-gray-600 focus:outline-none focus:border-[var(--color-neon-blue)] transition-colors shadow-lg"
                        disabled={isLoading}
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="absolute left-3 top-1/2 -translate-y-1/2 p-2 rounded-full text-gray-400 hover:text-white transition-colors"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m18.375 12.739-7.693 7.693a4.5 4.5 0 0 1-6.364-6.364l10.94-10.94A3 3 0 1 1 19.5 7.372L8.552 18.32m.009-.01-.01.01m5.699-9.941-7.81 7.81a1.5 1.5 0 0 0 2.112 2.13" />
                        </svg>
                    </button>
                    <button
                        onClick={handleSendMessage}
                        disabled={isLoading || !input.trim()}
                        className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-[var(--color-neon-blue)] text-black hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
                        </svg>
                    </button>
                </div>
            </div>
        </section>
    );
}
