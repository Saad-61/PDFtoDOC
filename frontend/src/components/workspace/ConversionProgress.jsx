import React from "react";
import {
  UploadCloud,
  FileSearch,
  Cpu,
  FileCheck2,
  XCircle,
  Clock,
  Sparkles,
} from "lucide-react";
import { Progress } from "../ui/progress";
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../ui/card";
import { NumberCounter } from "../bits/NumberCounter";

export function ConversionProgress({
  fileName,
  uploadPercent = 0,
  conversionStage = "UPLOADING",
  currentPage = 0,
  totalPages = 1,
  totalPercent = 0,
  elapsedSeconds = 0,
  onCancel,
}) {
  const steps = [
    {
      id: "upload",
      name: "File Transmission",
      desc: uploadPercent < 100 ? `Uploading (${uploadPercent}%)` : "Uploaded",
      icon: UploadCloud,
      active: conversionStage === "UPLOADING",
      completed: uploadPercent === 100 || totalPercent > 10,
    },
    {
      id: "parse",
      name: "Document Topology",
      desc: "Analyzing margins, fonts & styles",
      icon: FileSearch,
      active: conversionStage === "PARSING",
      completed: totalPercent > 20,
    },
    {
      id: "reconstruct",
      name: "Layout Reconstruction",
      desc: totalPages > 0 ? `Reconstructing page ${currentPage} of ${totalPages}` : "Reconstructing elements",
      icon: Cpu,
      active: conversionStage === "RECONSTRUCTING" || (totalPercent >= 20 && totalPercent < 90),
      completed: totalPercent >= 90,
    },
    {
      id: "package",
      name: "Word Packaging",
      desc: "Assembling .docx OpenXML binary",
      icon: FileCheck2,
      active: totalPercent >= 90,
      completed: totalPercent === 100,
    },
  ];

  return (
    <Card className="w-full max-w-2xl mx-auto border-slate-border shadow-2xl">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <span className="text-[11px] font-mono tracking-widest uppercase text-gold-400 font-semibold flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-gold-400 animate-ping" />
            Active Reconstruction
          </span>
          <CardTitle className="text-2xl mt-0.5">Reconstructing Document</CardTitle>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-carbon-900 border border-slate-border rounded-sm text-xs font-mono text-taupe">
          <Clock className="w-3.5 h-3.5 text-gold-400" />
          <span>{elapsedSeconds}s</span>
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-4">
        {/* Main Percentage & Filename Card */}
        <div className="p-4 rounded-md bg-carbon-900 border border-slate-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-taupe line-clamp-1 break-all max-w-[70%]" title={fileName}>
              {fileName}
            </span>
            <span className="text-xl font-mono font-bold text-gold-400">
              <NumberCounter value={totalPercent} suffix="%" />
            </span>
          </div>

          <Progress value={totalPercent} className="h-3 shadow-inner" />
        </div>

        {/* 4-Stage Editorial Stepper */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={step.id}
                className={`p-3.5 rounded-sm border transition-all flex items-start gap-3 ${
                  step.active
                    ? "border-gold-500 bg-carbon-750/90 shadow-gold-glow"
                    : step.completed
                    ? "border-slate-border bg-carbon-900/90 text-taupe"
                    : "border-slate-border/50 bg-carbon-900/30 opacity-40"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-sm flex items-center justify-center flex-shrink-0 mt-0.5 ${
                    step.active
                      ? "bg-gold-500 text-carbon-950 font-bold"
                      : step.completed
                      ? "bg-carbon-700 text-gold-400 border border-slate-border"
                      : "bg-carbon-800 text-dim"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-ivory flex items-center gap-1.5">
                    <span className="font-mono text-[10px] text-dim">{idx + 1}.</span>
                    {step.name}
                  </div>
                  <div className="text-[11px] text-taupe mt-0.5 line-clamp-1 font-mono">
                    {step.desc}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-between bg-carbon-850/50">
        <span className="text-xs font-mono text-dim flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-gold-500" />
          Processing with isolated memory worker
        </span>
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            className="text-oxblood-light hover:text-ivory hover:bg-oxblood/20"
          >
            <XCircle className="w-3.5 h-3.5 mr-1.5" />
            Cancel
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
