import React from "react";
import { ShieldCheck, Lock, FileCheck2, Terminal } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-border/50 bg-carbon-950/80 py-10 mt-auto">
      <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-taupe">
        {/* Editorial Statement */}
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 rounded-full bg-carbon-850 border border-gold-500/30 flex items-center justify-center text-gold-400">
            <ShieldCheck className="w-3.5 h-3.5" />
          </div>
          <span className="font-serif italic text-ivory">
            Autonomous Layout Reconstruction • Zero Server Retention
          </span>
        </div>

        {/* Shortcuts & Privacy Pillars */}
        <div className="flex flex-wrap items-center gap-6 text-dim font-mono text-[11px]">
          <span className="flex items-center gap-1.5">
            <kbd className="px-1.5 py-0.5 bg-carbon-900 border border-slate-border text-gold-400 rounded">
              Ctrl+V
            </kbd>
            Paste PDF
          </span>
          <span className="flex items-center gap-1.5">
            <Lock className="w-3 h-3 text-gold-500/70" />
            AES-256 Decryption Support
          </span>
          <span className="flex items-center gap-1.5">
            <FileCheck2 className="w-3 h-3 text-gold-500/70" />
            Native OpenXML (.docx)
          </span>
        </div>
      </div>
    </footer>
  );
}
