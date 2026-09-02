/**
 * Formats raw byte counts into human-readable strings (e.g., 2.45 MB).
 */
export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return "0 Bytes";
  if (!bytes || isNaN(bytes)) return "—";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

/**
 * Validates whether a file has a valid PDF MIME type or extension.
 */
export function isPdfFile(file) {
  if (!file) return false;
  const name = file.name || "";
  const type = file.type || "";
  return name.toLowerCase().endsWith(".pdf") || type === "application/pdf";
}

/**
 * Strips .pdf and returns .docx equivalent.
 */
export function getWordFilename(pdfName) {
  if (!pdfName) return "document.docx";
  if (pdfName.toLowerCase().endsWith(".pdf")) {
    return pdfName.slice(0, -4) + ".docx";
  }
  return pdfName + ".docx";
}
