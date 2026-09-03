import React, { useState } from "react";
import {
  FileText,
  Lock,
  Unlock,
  Layers,
  ArrowRight,
  RotateCcw,
} from "lucide-react";
import { formatBytes } from "../../utils/fileHelpers";
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../ui/card";
import { Badge } from "../ui/badge";

export function FilePreviewCard({
  file,
  preflightData,
  isPreflightLoading,
  onStartConversion,
  onReset,
  onOpenPasswordModal,
  password,
}) {
  const [rangeMode, setRangeMode] = useState("all"); // "all" | "custom"
  const [customRange, setCustomRange] = useState("");

  const numPages = preflightData?.numPages || 1;
  const isEncrypted = preflightData?.isEncrypted;
  const hasPassword = Boolean(password);

  const handleConvertClick = () => {
    const pageRange = rangeMode === "custom" ? customRange.trim() : null;
    onStartConversion({ pageRange });
  };

  return (
    <Card className="w-full max-w-2xl mx-auto border-slate-border shadow-2xl">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <span className="text-[11px] font-mono tracking-widest uppercase text-gold-400 font-semibold">
            Pre-Flight Inspection
          </span>
          <CardTitle className="text-2xl mt-0.5">Document Ready</CardTitle>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onReset}
          className="text-taupe hover:text-ivory"
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
          Choose Another
        </Button>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Document Metadata & Thumbnail Row */}
        <div className="flex flex-col sm:flex-row gap-5 p-4 rounded-md bg-carbon-900 border border-slate-border">
          {/* Page 1 Thumbnail Canvas / Fallback */}
          <div className="w-24 h-32 flex-shrink-0 bg-carbon-950 border border-slate-border rounded-sm overflow-hidden flex items-center justify-center relative shadow-inner">
            {isPreflightLoading ? (
              <div className="flex flex-col items-center gap-2">
                <div className="w-5 h-5 border-2 border-gold-500/30 border-t-gold-500 rounded-full animate-spin" />
                <span className="text-[9px] font-mono text-taupe">Scanning</span>
              </div>
            ) : preflightData?.thumbnailUrl ? (
              <img
                src={preflightData.thumbnailUrl}
                alt="Document preview"
                className="w-full h-full object-cover object-top"
              />
            ) : (
              <FileText className="w-10 h-10 text-gold-500/50" />
            )}
            <div className="absolute bottom-1 right-1 bg-carbon-950/90 border border-slate-border text-[9px] font-mono text-taupe px-1 py-0.2 rounded">
              P. 1
            </div>
          </div>

          {/* File Info */}
          <div className="flex-1 flex flex-col justify-between">
            <div>
              <h4
                className="text-base font-medium text-ivory line-clamp-1 break-all"
                title={file.name}
              >
                {file.name}
              </h4>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <Badge variant="default">{formatBytes(file.size)}</Badge>
                {numPages > 0 && (
                  <Badge variant="gold">
                    <Layers className="w-3 h-3 mr-1" />
                    {numPages} {numPages === 1 ? "Page" : "Pages"}
                  </Badge>
                )}
                {isEncrypted && (
                  <Badge variant={hasPassword ? "forest" : "brass"}>
                    {hasPassword ? (
                      <>
                        <Unlock className="w-3 h-3 mr-1 text-forest-light" />
                        Unlocked
                      </>
                    ) : (
                      <>
                        <Lock className="w-3 h-3 mr-1 text-brass" />
                        Encrypted
                      </>
                    )}
                  </Badge>
                )}
              </div>
            </div>

            {/* Password Prompt Alert if locked */}
            {isEncrypted && !hasPassword && (
              <div className="mt-3 p-2.5 bg-brass-surface border border-brass/30 rounded-sm flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-brass">
                  <Lock className="w-4 h-4 flex-shrink-0" />
                  <span>Document requires password to convert</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onOpenPasswordModal}
                  className="h-7 text-xs border-brass/50 text-brass hover:bg-brass/10"
                >
                  Enter Password
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Page Range Selector */}
        <div className="p-4 rounded-md bg-carbon-900/60 border border-slate-border/80 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-mono uppercase tracking-wider text-taupe flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-gold-400" />
              Page Extraction Scope
            </label>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setRangeMode("all")}
              className={`p-3 text-left rounded-sm border transition-all ${
                rangeMode === "all"
                  ? "border-gold-500 bg-carbon-800 text-ivory shadow-sm"
                  : "border-slate-border bg-carbon-900 text-taupe hover:text-ivory hover:border-slate-border-light"
              }`}
            >
              <div className="text-sm font-medium">All Pages</div>
              <div className="text-[11px] text-dim mt-0.5">
                Convert entire document ({numPages || 1} pages)
              </div>
            </button>

            <button
              type="button"
              onClick={() => setRangeMode("custom")}
              className={`p-3 text-left rounded-sm border transition-all ${
                rangeMode === "custom"
                  ? "border-gold-500 bg-carbon-800 text-ivory shadow-sm"
                  : "border-slate-border bg-carbon-900 text-taupe hover:text-ivory hover:border-slate-border-light"
              }`}
            >
              <div className="text-sm font-medium">Custom Range</div>
              <div className="text-[11px] text-dim mt-0.5">
                Select specific pages (e.g. 1-3, 5)
              </div>
            </button>
          </div>

          {rangeMode === "custom" && (
            <div className="pt-2 animate-in fade-in duration-150">
              <input
                type="text"
                value={customRange}
                onChange={(e) => setCustomRange(e.target.value)}
                placeholder={`e.g. 1-2, 4 (max ${numPages || 1})`}
                className="w-full px-3.5 py-2 text-sm bg-carbon-950 border border-slate-border focus:border-gold-500 focus:outline-none rounded-sm text-ivory placeholder:text-dim font-mono"
              />
              <span className="text-[11px] text-dim mt-1 block">
                Separate page ranges with commas. Example: <code className="text-gold-400">1-5, 8</code>
              </span>
            </div>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-carbon-850/50">
        <span className="text-xs font-mono text-dim">
          Outputs Microsoft Word (.docx) format
        </span>
        <Button
          onClick={handleConvertClick}
          disabled={isEncrypted && !hasPassword}
          size="lg"
          className="w-full sm:w-auto"
        >
          <FileText className="w-4 h-4 mr-2" />
          Reconstruct in Word (DOCX)
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </CardFooter>
    </Card>
  );
}
