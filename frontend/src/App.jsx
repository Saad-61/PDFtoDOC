import React, { useState, useEffect, useRef } from "react";
import { Header } from "./components/workspace/Header";
import { Footer } from "./components/workspace/Footer";
import { Dropzone } from "./components/workspace/Dropzone";
import { FilePreviewCard } from "./components/workspace/FilePreviewCard";
import { ConversionProgress } from "./components/workspace/ConversionProgress";
import { ResultCard } from "./components/workspace/ResultCard";
import { ErrorBanner } from "./components/workspace/ErrorBanner";
import { PasswordModal } from "./components/workspace/PasswordModal";
import { BatchQueue } from "./components/workspace/BatchQueue";
import { SmoothReveal } from "./components/bits/SmoothReveal";

import { usePdfPreflight } from "./hooks/usePdfPreflight";
import {
  createConversionJob,
  subscribeToJobEvents,
  convertPdfStream,
  apiClient,
} from "./services/api";
import { triggerBlobDownload } from "./utils/download";

export function App() {
  const [mode, setMode] = useState("single"); // "single" | "batch"
  const [workspaceState, setWorkspaceState] = useState("IDLE"); // "IDLE" | "PREVIEW" | "CONVERTING" | "COMPLETED" | "ERROR"

  // Active Single Document State
  const [selectedFile, setSelectedFile] = useState(null);
  const [password, setPassword] = useState("");
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Conversion Progress State
  const [progressState, setProgressState] = useState({
    uploadPercent: 0,
    stage: "UPLOADING",
    currentPage: 0,
    totalPages: 1,
    totalPercent: 0,
    elapsedSeconds: 0,
  });

  // Conversion Result State
  const [resultState, setResultState] = useState({
    docxBlob: null,
    docxFilename: "",
    pagesConverted: 1,
    durationSeconds: null,
  });

  const {
    loading: isPreflightLoading,
    preflightData,
    analyzePdf,
    resetPreflight,
  } = usePdfPreflight();

  const timerRef = useRef(null);
  const sseUnsubscribeRef = useRef(null);

  // Clean up timer and SSE on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (sseUnsubscribeRef.current) sseUnsubscribeRef.current();
    };
  }, []);

  // Handle Initial File Selection
  const handleFileSelected = async (file) => {
    setSelectedFile(file);
    setPassword("");
    setErrorMessage(null);
    setWorkspaceState("PREVIEW");

    const data = await analyzePdf(file);
    if (data?.isEncrypted) {
      setIsPasswordModalOpen(true);
    }
  };

  // Password submission handler
  const handlePasswordSubmit = async (enteredPassword) => {
    setPassword(enteredPassword);
    if (selectedFile) {
      await analyzePdf(selectedFile, enteredPassword);
    }
  };

  // Start Real-Time Conversion Workflow
  const handleStartConversion = async ({ pageRange = null }) => {
    if (!selectedFile) return;

    setWorkspaceState("CONVERTING");
    setErrorMessage(null);

    const startTime = Date.now();
    setProgressState({
      uploadPercent: 0,
      stage: "UPLOADING",
      currentPage: 0,
      totalPages: preflightData?.numPages || 1,
      totalPercent: 5,
      elapsedSeconds: 0,
    });

    // Start elapsed timer
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setProgressState((prev) => ({ ...prev, elapsedSeconds: elapsed }));
    }, 1000);

    try {
      // Step 1: Create Job
      const job = await createConversionJob({
        file: selectedFile,
        password: password,
        pageRange: pageRange,
        onUploadProgress: (percent) => {
          setProgressState((prev) => ({
            ...prev,
            uploadPercent: percent,
            totalPercent: Math.min(15, Math.round(percent * 0.15)),
            stage: percent < 100 ? "UPLOADING" : "PARSING",
          }));
        },
      });

      // Step 2: Subscribe to Real-Time SSE Stream
      const unsubscribe = subscribeToJobEvents({
        jobId: job.job_id,
        onProgress: (event) => {
          setProgressState((prev) => ({
            ...prev,
            stage: event.stage || "RECONSTRUCTING",
            currentPage: event.current_page || prev.currentPage,
            totalPages: event.total_pages || prev.totalPages,
            totalPercent: event.percent || prev.totalPercent,
          }));
        },
        onComplete: async (event) => {
          if (timerRef.current) clearInterval(timerRef.current);

          // Fetch the final completed DOCX binary
          try {
            const downloadRes = await apiClient.get(
              `/api/v1/jobs/${job.job_id}/download`,
              { responseType: "blob" }
            );

            const docxFilename = selectedFile.name.replace(/\.pdf$/i, ".docx");
            const duration = Math.round(((Date.now() - startTime) / 1000) * 10) / 10;

            setResultState({
              docxBlob: downloadRes.data,
              docxFilename,
              pagesConverted: event.total_pages || preflightData?.numPages || 1,
              durationSeconds: duration,
            });

            setWorkspaceState("COMPLETED");

            // Auto-trigger download
            triggerBlobDownload(downloadRes.data, docxFilename);
          } catch (dlErr) {
            console.error("Failed to download converted document:", dlErr);
            setErrorMessage("Failed to retrieve converted document binary.");
            setWorkspaceState("ERROR");
          }
        },
        onError: (err) => {
          if (timerRef.current) clearInterval(timerRef.current);
          console.error("SSE Conversion error:", err);
          setErrorMessage(err.message || "Conversion failed during reconstruction.");
          setWorkspaceState("ERROR");
        },
      });

      sseUnsubscribeRef.current = unsubscribe;
    } catch (err) {
      if (timerRef.current) clearInterval(timerRef.current);
      console.error("Failed to enqueue conversion job:", err);
      const msg =
        err.response?.data?.error?.message ||
        "Failed to initiate conversion. Please verify document formatting.";
      setErrorMessage(msg);
      setWorkspaceState("ERROR");
    }
  };

  // Reset workspace
  const handleReset = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (sseUnsubscribeRef.current) sseUnsubscribeRef.current();
    setSelectedFile(null);
    setPassword("");
    setErrorMessage(null);
    resetPreflight();
    setWorkspaceState("IDLE");
  };

  // Download Action
  const handleDownload = () => {
    if (resultState.docxBlob) {
      triggerBlobDownload(resultState.docxBlob, resultState.docxFilename);
    }
  };

  return (
    <div className="min-h-screen bg-carbon-900 bg-grain flex flex-col text-ivory">
      {/* Top Header */}
      <Header mode={mode} setMode={setMode} />

      {/* Main Workspace Stage */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-12 flex flex-col items-center justify-center">
        {mode === "batch" ? (
          <SmoothReveal key="batch-mode" className="w-full">
            <BatchQueue />
          </SmoothReveal>
        ) : (
          <div className="w-full space-y-6">
            {/* Error Banner */}
            {workspaceState === "ERROR" && (
              <SmoothReveal key="error-banner">
                <ErrorBanner
                  error={errorMessage}
                  onReset={handleReset}
                  onPasswordRequired={() => setIsPasswordModalOpen(true)}
                />
              </SmoothReveal>
            )}

            {/* Ingestion Dropzone */}
            {workspaceState === "IDLE" && (
              <SmoothReveal key="dropzone-idle">
                <Dropzone onFileSelected={handleFileSelected} />
              </SmoothReveal>
            )}

            {/* Document Preflight & Configuration Card */}
            {workspaceState === "PREVIEW" && selectedFile && (
              <SmoothReveal key="preview-card">
                <FilePreviewCard
                  file={selectedFile}
                  preflightData={preflightData}
                  isPreflightLoading={isPreflightLoading}
                  onStartConversion={handleStartConversion}
                  onReset={handleReset}
                  onOpenPasswordModal={() => setIsPasswordModalOpen(true)}
                  password={password}
                />
              </SmoothReveal>
            )}

            {/* Real-Time Conversion Stepper */}
            {workspaceState === "CONVERTING" && selectedFile && (
              <SmoothReveal key="converting-card">
                <ConversionProgress
                  fileName={selectedFile.name}
                  uploadPercent={progressState.uploadPercent}
                  conversionStage={progressState.stage}
                  currentPage={progressState.currentPage}
                  totalPages={progressState.totalPages}
                  totalPercent={progressState.totalPercent}
                  elapsedSeconds={progressState.elapsedSeconds}
                  onCancel={handleReset}
                />
              </SmoothReveal>
            )}

            {/* Successful Result Card */}
            {workspaceState === "COMPLETED" && (
              <SmoothReveal key="result-card">
                <ResultCard
                  fileName={selectedFile?.name}
                  docxFilename={resultState.docxFilename}
                  originalSize={selectedFile?.size}
                  docxBlob={resultState.docxBlob}
                  pagesConverted={resultState.pagesConverted}
                  durationSeconds={resultState.durationSeconds}
                  onDownload={handleDownload}
                  onReset={handleReset}
                />
              </SmoothReveal>
            )}
          </div>
        )}
      </main>

      {/* Password Modal */}
      <PasswordModal
        open={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSubmitPassword={handlePasswordSubmit}
        fileName={selectedFile?.name || "document.pdf"}
      />

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
