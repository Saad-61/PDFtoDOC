import React, { useState, useRef, useEffect } from "react";
import { UploadCloud, FilePlus } from "lucide-react";
import { isPdfFile } from "../../utils/fileHelpers";
import { ShimmerBorder } from "../bits/ShimmerBorder";
import { Button } from "../ui/button";

export function Dropzone({ onFileSelected, isProcessing = false }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Global Clipboard Paste Listener (Ctrl+V)
  useEffect(() => {
    const handlePaste = (e) => {
      if (isProcessing) return;
      if (e.clipboardData && e.clipboardData.files.length > 0) {
        const file = e.clipboardData.files[0];
        if (isPdfFile(file)) {
          e.preventDefault();
          onFileSelected(file);
        }
      }
    };

    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, [onFileSelected, isProcessing]);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isProcessing) setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (isProcessing) return;

    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (isPdfFile(file)) {
        onFileSelected(file);
      } else {
        alert("Please upload a valid PDF document (.pdf).");
      }
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (isPdfFile(file)) {
        onFileSelected(file);
      }
      e.target.value = "";
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="w-full max-w-2xl mx-auto"
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        accept=".pdf,application/pdf"
        className="hidden"
      />

      <ShimmerBorder
        active={isDragOver}
        borderRadius="rounded-md"
        className="w-full transition-all duration-200"
      >
        <div
          onClick={() => !isProcessing && fileInputRef.current?.click()}
          className={`relative cursor-pointer p-10 sm:p-14 border border-dashed rounded-md transition-all duration-200 flex flex-col items-center justify-center text-center select-none ${
            isDragOver
              ? "border-gold-500 bg-carbon-750 scale-[1.005]"
              : "border-slate-border hover:border-gold-500/60 bg-carbon-800/80 hover:bg-carbon-800"
          }`}
        >
          {/* Subtle gold decorative corner accents */}
          <div className="absolute top-2 left-2 w-2.5 h-2.5 border-t border-l border-gold-500/50" />
          <div className="absolute top-2 right-2 w-2.5 h-2.5 border-t border-r border-gold-500/50" />
          <div className="absolute bottom-2 left-2 w-2.5 h-2.5 border-b border-l border-gold-500/50" />
          <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r border-gold-500/50" />

          {/* Central Ingestion Icon */}
          <div
            className={`w-16 h-16 rounded-full flex items-center justify-center mb-5 transition-transform duration-300 ${
              isDragOver
                ? "bg-gold-500 text-carbon-950 scale-110"
                : "bg-carbon-700 text-gold-400 border border-slate-border group-hover:scale-105"
            }`}
          >
            <UploadCloud className="w-8 h-8" />
          </div>

          <h2 className="font-display text-3xl font-semibold text-ivory tracking-tight mb-2">
            Select or Drop Your PDF
          </h2>
          <p className="text-sm text-taupe max-w-md mb-6 leading-relaxed">
            Drag your file here, browse your device, or simply press{" "}
            <kbd className="px-1.5 py-0.5 font-mono text-xs bg-carbon-900 border border-slate-border text-gold-400 rounded-sm">
              Ctrl + V
            </kbd>{" "}
            anywhere to paste.
          </p>

          <Button
            type="button"
            variant="default"
            size="lg"
            className="pointer-events-none"
          >
            <FilePlus className="w-4 h-4 mr-2" />
            Browse PDF Document
          </Button>

          {/* Document constraints metadata */}
          <div className="mt-8 pt-5 border-t border-slate-border/50 flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-dim">
            <span className="flex items-center gap-1.5">
              <span className="w-1 h-1 rounded-full bg-gold-500" />
              Preserves Native Tables & Formatting
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-1 h-1 rounded-full bg-gold-500" />
              Up to 50MB & 250 Pages
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-1 h-1 rounded-full bg-gold-500" />
              Zero Data Retention
            </span>
          </div>
        </div>
      </ShimmerBorder>
    </div>
  );
}
