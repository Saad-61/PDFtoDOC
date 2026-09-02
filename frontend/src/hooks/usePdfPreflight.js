import { useState, useCallback } from "react";
import * as pdfjsLib from "pdfjs-dist";

// Configure pdfjs worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;

export function usePdfPreflight() {
  const [loading, setLoading] = useState(false);
  const [preflightData, setPreflightData] = useState(null);
  const [error, setError] = useState(null);

  const analyzePdf = useCallback(async (file, password = "") => {
    if (!file) return null;
    setLoading(true);
    setError(null);

    try {
      const arrayBuffer = await file.arrayBuffer();
      const loadingTask = pdfjsLib.getDocument({
        data: arrayBuffer,
        password: password || undefined,
      });

      // Handle password required callback
      loadingTask.onPassword = (callback, reason) => {
        setPreflightData((prev) => ({
          ...prev,
          isEncrypted: true,
          needsPassword: true,
          fileName: file.name,
          fileSize: file.size,
        }));
      };

      const pdf = await loadingTask.promise;
      const numPages = pdf.numPages;

      // Render thumbnail of page 1
      let thumbnailUrl = null;
      try {
        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: 0.5 });
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        await page.render({
          canvasContext: context,
          viewport: viewport,
        }).promise;

        thumbnailUrl = canvas.toDataURL("image/jpeg", 0.85);
      } catch (thumbErr) {
        console.warn("Failed to generate page 1 thumbnail:", thumbErr);
      }

      const data = {
        fileName: file.name,
        fileSize: file.size,
        numPages,
        thumbnailUrl,
        isEncrypted: false,
        needsPassword: false,
      };

      setPreflightData(data);
      setLoading(false);
      return data;
    } catch (err) {
      if (err.name === "PasswordException") {
        const data = {
          fileName: file.name,
          fileSize: file.size,
          numPages: 0,
          thumbnailUrl: null,
          isEncrypted: true,
          needsPassword: true,
        };
        setPreflightData(data);
        setLoading(false);
        return data;
      }

      console.error("PDF preflight analysis failed:", err);
      setError("Unable to read PDF structure. The file may be corrupt.");
      setLoading(false);
      return null;
    }
  }, []);

  const resetPreflight = useCallback(() => {
    setPreflightData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    loading,
    preflightData,
    error,
    analyzePdf,
    resetPreflight,
  };
}
