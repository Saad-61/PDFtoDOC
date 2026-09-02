import confetti from "canvas-confetti";

/**
 * Initiates an automatic browser file download from a Blob object.
 */
export function triggerBlobDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename || "converted_document.docx";
  document.body.appendChild(anchor);
  anchor.click();
  
  // Cleanup
  setTimeout(() => {
    document.body.removeChild(anchor);
    window.URL.revokeObjectURL(url);
  }, 200);
}

/**
 * Fires a subtle, refined gold celebration confetti.
 */
export function fireGoldConfetti() {
  confetti({
    particleCount: 45,
    spread: 60,
    origin: { y: 0.75 },
    colors: ["#C5A059", "#D4AF37", "#F5F4F0", "#AA863F"],
    ticks: 200,
    gravity: 1.1,
    scalar: 0.9,
    disableForReducedMotion: true,
  });
}
