import React, { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { fetchHealth } from "../../services/api";
import { Badge } from "../ui/badge";

export function Header({ mode, setMode }) {
  const [serverHealth, setServerHealth] = useState({ online: false, checking: true });

  useEffect(() => {
    let isMounted = true;
    const checkServer = async () => {
      try {
        const data = await fetchHealth();
        if (isMounted) {
          setServerHealth({ online: data.status === "healthy", checking: false, version: data.version });
        }
      } catch {
        if (isMounted) {
          setServerHealth({ online: false, checking: false });
        }
      }
    };

    checkServer();
    const interval = setInterval(checkServer, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="border-b border-slate-border bg-carbon-950/60 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Brand & Editorial Seal */}
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-sm bg-carbon-800 border border-slate-border flex items-center justify-center">
            <FileText className="w-5 h-5 text-gold-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display text-2xl font-bold tracking-tight text-ivory">
                PDF <span className="text-gold-400 font-serif italic text-xl">to</span> DOCX
              </h1>
              <span className="text-[10px] uppercase tracking-widest font-mono text-dim border border-slate-border px-1.5 py-0.5 rounded-sm">
                v1.0
              </span>
            </div>
            <p className="text-xs text-taupe tracking-tight">
              High-Fidelity Document Layout Reconstructor
            </p>
          </div>
        </div>

        {/* Mode Toggle & System Status */}
        <div className="flex items-center gap-4">
          {/* Mode Switcher */}
          <div className="hidden sm:flex bg-carbon-800 border border-slate-border p-1 rounded-sm">
            <button
              onClick={() => setMode("single")}
              className={`px-3 py-1 text-xs font-medium rounded-sm transition-all ${
                mode === "single"
                  ? "bg-gold-500 text-carbon-950 font-semibold shadow-sm"
                  : "text-taupe hover:text-ivory"
              }`}
            >
              Single Document
            </button>
            <button
              onClick={() => setMode("batch")}
              className={`px-3 py-1 text-xs font-medium rounded-sm transition-all ${
                mode === "batch"
                  ? "bg-gold-500 text-carbon-950 font-semibold shadow-sm"
                  : "text-taupe hover:text-ivory"
              }`}
            >
              Batch Queue
            </button>
          </div>

          {/* Telemetry Status Indicator */}
          <div className="flex items-center gap-2">
            {serverHealth.checking ? (
              <Badge variant="default" className="text-[11px] py-1">
                <span className="w-1.5 h-1.5 rounded-full bg-taupe animate-pulse" />
                Connecting...
              </Badge>
            ) : serverHealth.online ? (
              <Badge variant="forest" className="text-[11px] py-1 border-forest-light/30">
                <span className="w-1.5 h-1.5 rounded-full bg-forest-light animate-pulse" />
                Engine Online
              </Badge>
            ) : (
              <Badge variant="oxblood" className="text-[11px] py-1">
                <span className="w-1.5 h-1.5 rounded-full bg-oxblood-light" />
                Engine Offline
              </Badge>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
