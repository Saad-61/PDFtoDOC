import React, { useState } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Download,
  Trash2,
  Play,
  Loader2,
} from "lucide-react";
import { formatBytes, isPdfFile } from "../../utils/fileHelpers";
import { convertPdfStream } from "../../services/api";
import { triggerBlobDownload } from "../../utils/download";
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../ui/card";
import { Progress } from "../ui/progress";

export function BatchQueue() {
  const [queue, setQueue] = useState([]);
  const [isProcessingBatch, setIsProcessingBatch] = useState(false);

  const handleFilesAdded = (files) => {
    const validPdfs = Array.from(files).filter(isPdfFile);
    if (validPdfs.length === 0) return;

    const newItems = validPdfs.map((file) => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      file,
      name: file.name,
      size: file.size,
      status: "QUEUED", // "QUEUED" | "CONVERTING" | "COMPLETED" | "FAILED"
      percent: 0,
      docxBlob: null,
      docxFilename: file.name.replace(/\.pdf$/i, ".docx"),
      error: null,
    }));

    setQueue((prev) => [...prev, ...newItems]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      handleFilesAdded(e.dataTransfer.files);
    }
  };

  const removeItem = (id) => {
    setQueue((prev) => prev.filter((item) => item.id !== id));
  };

  const clearCompleted = () => {
    setQueue((prev) => prev.filter((item) => item.status !== "COMPLETED"));
  };

  const startBatchConversion = async () => {
    setIsProcessingBatch(true);

    for (let i = 0; i < queue.length; i++) {
      const item = queue[i];
      if (item.status === "COMPLETED") continue;

      // Update state to CONVERTING
      setQueue((prev) =>
        prev.map((it) => (it.id === item.id ? { ...it, status: "CONVERTING", percent: 10 } : it))
      );

      try {
        const result = await convertPdfStream({
          file: item.file,
          onUploadProgress: (pct) => {
            setQueue((prev) =>
              prev.map((it) =>
                it.id === item.id ? { ...it, percent: Math.min(85, Math.max(15, pct)) } : it
              )
            );
          },
        });

        setQueue((prev) =>
          prev.map((it) =>
            it.id === item.id
              ? {
                  ...it,
                  status: "COMPLETED",
                  percent: 100,
                  docxBlob: result.blob,
                  docxFilename: result.filename,
                }
              : it
          )
        );
      } catch (err) {
        console.error(`Batch item failed: ${item.name}`, err);
        setQueue((prev) =>
          prev.map((it) =>
            it.id === item.id
              ? {
                  ...it,
                  status: "FAILED",
                  error: err.response?.data?.error?.message || "Conversion failed",
                }
              : it
          )
        );
      }
    }

    setIsProcessingBatch(false);
  };

  const downloadAllCompleted = () => {
    const completed = queue.filter((item) => item.status === "COMPLETED" && item.docxBlob);
    completed.forEach((item, idx) => {
      setTimeout(() => {
        triggerBlobDownload(item.docxBlob, item.docxFilename);
      }, idx * 250);
    });
  };

  const completedCount = queue.filter((item) => item.status === "COMPLETED").length;
  const queuedCount = queue.filter((item) => item.status === "QUEUED").length;

  return (
    <Card className="w-full max-w-4xl mx-auto border-slate-border shadow-2xl">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <span className="text-[11px] font-mono tracking-widest uppercase text-gold-400 font-semibold">
            Batch Processing
          </span>
          <CardTitle className="text-2xl mt-0.5">Multi-Document Queue</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          {completedCount > 0 && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={downloadAllCompleted}
                className="text-xs"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" />
                Download All ({completedCount})
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearCompleted}
                disabled={isProcessingBatch}
                className="text-xs text-taupe hover:text-ivory"
              >
                Clear Completed
              </Button>
            </>
          )}
          {queue.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setQueue([])}
              disabled={isProcessingBatch}
              className="text-xs text-taupe hover:text-ivory"
            >
              Clear All
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Batch Dropzone Target */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="p-6 border border-dashed border-slate-border hover:border-gold-500/60 rounded-md bg-carbon-900/60 flex flex-col items-center justify-center text-center cursor-pointer transition-all"
          onClick={() => document.getElementById("batch-file-input")?.click()}
        >
          <input
            id="batch-file-input"
            type="file"
            multiple
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={(e) => e.target.files && handleFilesAdded(e.target.files)}
          />
          <UploadCloud className="w-8 h-8 text-gold-400 mb-2" />
          <p className="text-sm font-medium text-ivory">
            Drop multiple PDF documents here or click to browse
          </p>
          <span className="text-xs font-mono text-dim mt-1">
            Queue as many files as needed • Sequential isolated conversions
          </span>
        </div>

        {/* Queue Items Table */}
        {queue.length > 0 && (
          <div className="border border-slate-border rounded-sm overflow-hidden bg-carbon-900">
            <div className="p-3 bg-carbon-850 border-b border-slate-border flex items-center justify-between text-xs font-mono text-taupe">
              <span>{queue.length} Documents in Queue</span>
              <span>
                {completedCount} of {queue.length} completed
              </span>
            </div>

            <div className="divide-y divide-slate-border/50 max-h-96 overflow-y-auto">
              {queue.map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 flex items-center justify-between gap-4 hover:bg-carbon-800/50 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <FileText className="w-5 h-5 text-gold-400 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <div className="text-xs font-medium text-ivory truncate" title={item.name}>
                        {item.name}
                      </div>
                      <div className="text-[11px] font-mono text-dim flex items-center gap-2 mt-0.5">
                        <span>{formatBytes(item.size)}</span>
                        {item.status === "CONVERTING" && (
                          <span className="text-gold-400 flex items-center gap-1">
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Converting...
                          </span>
                        )}
                        {item.status === "COMPLETED" && (
                          <span className="text-forest-light flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            Ready
                          </span>
                        )}
                        {item.status === "FAILED" && (
                          <span className="text-oxblood-light flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" />
                            {item.error || "Failed"}
                          </span>
                        )}
                      </div>
                      {item.status === "CONVERTING" && (
                        <Progress value={item.percent} className="h-1.5 mt-2" />
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {item.status === "COMPLETED" && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => triggerBlobDownload(item.docxBlob, item.docxFilename)}
                        className="h-8 text-xs font-semibold px-3"
                      >
                        <Download className="w-3.5 h-3.5 mr-1" />
                        Download
                      </Button>
                    )}
                    <button
                      type="button"
                      disabled={isProcessingBatch && item.status === "CONVERTING"}
                      onClick={() => removeItem(item.id)}
                      className="p-1.5 text-taupe hover:text-oxblood-light rounded transition-colors disabled:opacity-30"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between bg-carbon-850/50">
        <span className="text-xs font-mono text-dim">
          Preserves original document formatting per file
        </span>
        <Button
          onClick={startBatchConversion}
          disabled={isProcessingBatch || queuedCount === 0}
          size="default"
        >
          {isProcessingBatch ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Processing Batch...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Start Batch Conversion ({queuedCount})
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
