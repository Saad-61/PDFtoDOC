import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : "";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutes timeout for heavy conversions
});

/**
 * Parses filename from Content-Disposition header (RFC 5987 aware).
 */
export function extractFilenameFromHeader(header, fallback = "converted_document.docx") {
  if (!header) return fallback;

  // Check RFC 5987 filename*=UTF-8''...
  const utf8Match = header.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match && utf8Match[1]) {
    try {
      return decodeURIComponent(utf8Match[1]);
    } catch {
      // fallback
    }
  }

  // Check standard filename="..."
  const stdMatch = header.match(/filename="?([^";]+)"?/i);
  if (stdMatch && stdMatch[1]) {
    return stdMatch[1];
  }

  return fallback;
}

/**
 * Validates PDF metadata & password status without starting full conversion.
 */
export async function validatePdf(file, password = "") {
  const formData = new FormData();
  formData.append("file", file);
  if (password) {
    formData.append("password", password);
  }

  const response = await apiClient.post("/api/v1/convert/validate", formData);
  return response.data;
}

/**
 * Synchronous direct stream conversion (ideal for fast conversions).
 */
export async function convertPdfStream({
  file,
  password = "",
  pageRange = "",
  onUploadProgress = null,
  cancelToken = null,
}) {
  const formData = new FormData();
  formData.append("file", file);
  if (password) formData.append("password", password);
  if (pageRange) formData.append("page_range", pageRange);

  const response = await apiClient.post("/api/v1/convert/stream", formData, {
    responseType: "blob",
    cancelToken: cancelToken,
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(percent, progressEvent.loaded, progressEvent.total);
      }
    },
  });

  const contentDisposition = response.headers["content-disposition"];
  const filename = extractFilenameFromHeader(
    contentDisposition,
    file.name.replace(/\.pdf$/i, ".docx")
  );

  return {
    blob: response.data,
    filename,
  };
}

/**
 * Enqueues an asynchronous conversion job.
 */
export async function createConversionJob({
  file,
  password = "",
  pageRange = "",
  onUploadProgress = null,
}) {
  const formData = new FormData();
  formData.append("file", file);
  if (password) formData.append("password", password);
  if (pageRange) formData.append("page_range", pageRange);

  const response = await apiClient.post("/api/v1/convert/jobs", formData, {
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(percent);
      }
    },
  });

  return response.data;
}

/**
 * Subscribes to real-time Server-Sent Events for an active job.
 */
export function subscribeToJobEvents({
  jobId,
  onProgress,
  onComplete,
  onError,
}) {
  const sseUrl = `${API_BASE_URL}/api/v1/jobs/${jobId}/events`;
  const eventSource = new EventSource(sseUrl);

  eventSource.addEventListener("progress", (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onProgress) onProgress(data);

      if (data.status === "COMPLETED") {
        eventSource.close();
        if (onComplete) onComplete(data);
      } else if (data.status === "FAILED") {
        eventSource.close();
        if (onError) onError(new Error(data.error || "Conversion failed."));
      }
    } catch (err) {
      console.error("Failed to parse SSE message:", err);
    }
  });

  eventSource.onerror = (err) => {
    console.warn("SSE connection error/closed:", err);
    eventSource.close();
    if (onError) onError(err);
  };

  return () => {
    eventSource.close();
  };
}

/**
 * Retrieves download URL for a completed job.
 */
export function getJobDownloadUrl(jobId) {
  return `${API_BASE_URL}/api/v1/jobs/${jobId}/download`;
}

/**
 * Queries server telemetry.
 */
export async function fetchHealth() {
  const response = await apiClient.get("/api/v1/health");
  return response.data;
}
