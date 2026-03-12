import Image from "next/image";
import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  return (
    <div className="flex h-screen flex-col bg-[var(--background)] text-white font-sans selection:bg-cyan-500 selection:text-black">
      {/* Header */}
      <header className="glass-panel sticky top-0 z-50 flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 relative">
            <Image src="/logo.png" alt="The Council Logo" fill className="object-contain" />
          </div>
          <h1 className="text-xl font-bold tracking-wider uppercase text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
            The Council
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-500 uppercase tracking-widest">Autonomous Analytics</span>
          <div className="h-2 w-2 rounded-full bg-[var(--color-neon-green)] glow-green"></div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 glass-panel border-l-0 border-y-0 flex flex-col p-4 gap-4 hidden md:flex">
          <nav className="flex flex-col gap-2">
            <button className="flex items-center gap-3 p-3 rounded-lg hover:bg-[var(--color-surface-hover)] transition-colors text-sm text-gray-300 hover:text-white">
              <span className="w-2 h-2 rounded-full bg-[var(--color-neon-blue)]"></span>
              New Session
            </button>
            <div className="h-px bg-[var(--color-glass-border)] my-2"></div>
            <div className="text-xs text-gray-500 uppercase tracking-wider px-2 mb-2">History</div>
            {/* History items would go here */}
          </nav>
        </aside>

        {/* Chat Area */}
        <ChatInterface />

      </main>
    </div>
  );
}
