import React, { useEffect } from "react";
import {
  Download,
  CheckCircle2,
  FileCheck,
  RotateCcw,
  Clock,
  Layers,
  HardDrive,
  ShieldCheck,
} from "lucide-react";
import { formatBytes } from "../../utils/fileHelpers";
import { fireGoldConfetti } from "../../utils/download";
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../ui/card";
import { Badge } from "../ui/badge";

export function ResultCard({
  fileName,
  docxFilename,
  originalSize,
  docxBlob,
  docxUrl,
  pagesConverted,
  durationSeconds,
  onDownload,
  onReset,
}) {
  useEffect(() => {
    // Fire refined gold celebration particles upon successful conversion
    fireGoldConfetti();
  }, []);

  const docxSize = docxBlob ? docxBlob.size : null;

  return (
    <Card className="w-full max-w-2xl mx-auto border-gold-500/40">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <Badge variant="forest" className="mb-1 py-0.5">
            <CheckCircle2 className="w-3 h-3 mr-1 text-forest-light" />
            Reconstruction Complete
          </Badge>
          <CardTitle className="text-2xl mt-1">Word Document Ready</CardTitle>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onReset}
          className="text-taupe hover:text-ivory"
        >
          <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
          Convert Another
        </Button>
      </CardHeader>

      <CardContent className="space-y-6 pt-2">
        {/* Output File Details Banner */}
        <div className="p-5 rounded-md bg-carbon-900 border border-slate-border flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-12 h-12 rounded-sm bg-gold-500/10 border border-gold-500/30 flex items-center justify-center flex-shrink-0">
              <FileCheck className="w-6 h-6 text-gold-400" />
            </div>
            <div className="min-w-0">
              <h4 className="text-base font-semibold text-ivory line-clamp-1 break-all" title={docxFilename}>
                {docxFilename}
              </h4>
              <p className="text-xs font-mono text-dim mt-0.5">
                Microsoft Word OpenXML Document (.docx)
              </p>
            </div>
          </div>
          <Badge variant="gold" className="flex-shrink-0">
            DOCX
          </Badge>
        </div>

        {/* Conversion Performance Metrics */}
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3.5 rounded-sm bg-carbon-900 border border-slate-border text-center">
            <div className="flex items-center justify-center text-gold-400 mb-1">
              <Layers className="w-4 h-4" />
            </div>
            <div className="font-mono text-base font-bold text-ivory">
              {pagesConverted || 1}
            </div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-dim mt-0.5">
              Pages Preserved
            </div>
          </div>

          <div className="p-3.5 rounded-sm bg-carbon-900 border border-slate-border text-center">
            <div className="flex items-center justify-center text-gold-400 mb-1">
              <Clock className="w-4 h-4" />
            </div>
            <div className="font-mono text-base font-bold text-ivory">
              {durationSeconds ? `${durationSeconds}s` : "Fast"}
            </div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-dim mt-0.5">
              Execution Time
            </div>
          </div>

          <div className="p-3.5 rounded-sm bg-carbon-900 border border-slate-border text-center">
            <div className="flex items-center justify-center text-gold-400 mb-1">
              <HardDrive className="w-4 h-4" />
            </div>
            <div className="font-mono text-base font-bold text-ivory">
              {docxSize ? formatBytes(docxSize) : "Optimized"}
            </div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-dim mt-0.5">
              Docx Size
            </div>
          </div>
        </div>

        {/* Primary Download CTA */}
        <Button
          onClick={onDownload}
          size="lg"
          className="w-full h-14 text-base font-bold"
        >
          <Download className="w-5 h-5 mr-2" />
          Download Word Document (.docx)
        </Button>
      </CardContent>

      <CardFooter className="flex items-center justify-between bg-carbon-850/50">
        <span className="text-xs font-mono text-dim flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-gold-400" />
          Temporary files automatically cleaned from server
        </span>
      </CardFooter>
    </Card>
  );
}
