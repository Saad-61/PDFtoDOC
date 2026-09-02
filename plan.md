# Project Blueprint: High-Performance PDF to DOCX Converter
**Stack:** Python (FastAPI) + React (Vite) + Tailwind CSS + shadcn/ui + React Bits  
**Design Aesthetic:** "Old Money" Editorial / Tactile Dark Heritage  
**Execution Target:** Autonomous AI Coding Agent & Production Deployment

---

## 1. Executive Summary & Core Value Proposition

This application provides an ultra-reliable, privacy-first, layout-preserving **PDF to DOCX Converter**. It pairs high-fidelity document layout reconstruction with an exquisite, distraction-free **"Old Money" tactile editorial interface**.

### Key Differentiators & Improvements over Standard Converters
1. **Dual Conversion Pipeline:**
   - **Fast Stream Path:** Instant streaming response for small documents (< 10 pages).
   - **Asynchronous SSE Job Path:** Real-time page-by-page progress callback (`"Reconstructing page 7 of 24 (29%)..."`) via Server-Sent Events (SSE) for larger documents, preventing HTTP connection timeouts.
2. **Process Isolation & Memory Guard:** Heavy conversions run in isolated worker processes (`ProcessPoolExecutor`) to prevent CPU starvation and isolate PyMuPDF C-level memory spikes from the FastAPI async event loop.
3. **Client-Side PDF Preflight & Preview:** Frontend renders instantaneous PDF thumbnails, page counts, and metadata using `pdfjs-dist` before uploading.
4. **Encrypted PDF Handling:** Gracefully detects password-locked PDFs and provides an inline unlocking modal.
5. **Batch Processing & Selective Page Ranges:** Convert full documents, custom page ranges (e.g. `1-5, 8, 12-15`), or batch queue multiple PDFs with "Download All as ZIP" capability.
6. **Zero-Trace Ephemeral Storage:** Guaranteed auto-cleanup via FastAPI background tasks and a fallback cron garbage collector that prunes temporary files older than 15 minutes.

---

## 2. Visual Identity & Design System: "Old Money" Aesthetic

Strictly avoids generic modern SaaS tropes (no translucent frosted glass, no neon cyan/purple gradients, no bubbly oversized radiuses). The interface feels understated, authoritative, tactile, and editorial—reminiscent of bespoke stationery, fine leather-bound ledger books, and vintage Swiss typography.

### 2.1 Color Palette & Theme Tokens
| Token Name | Hex Code | Purpose / Application |
| :--- | :--- | :--- |
| **Base Background** | `#121316` | Deep Matte Carbon primary canvas |
| **Surface (Level 1)** | `#1A1B1F` | Primary workspace cards & dropzones |
| **Surface (Level 2)** | `#222328` | Elevated modals, dropdowns, hovered items |
| **Border / Divider** | `#2E2F35` | Slate-bronze hairline borders (1px solid) |
| **Border Active / Focus**| `#C5A059` | Antique Gold fine border highlight on focus/drag |
| **Primary Accent** | `#C5A059` / `#D4AF37` | Warm Antique Gold / Champagne Gold for key CTAs & progress |
| **Primary Text** | `#F5F4F0` | Soft Ivory / Warm Cream for headings & body |
| **Secondary Text** | `#A8A69E` | Warm Taupe / Muted Silver for labels & descriptions |
| **Muted Metadata** | `#686660` | Dim Carbon for file sizes, timestamps, and captions |
| **Status: Success** | `#2D5A43` / `#3E7B5C` | Deep English Forest Green badge & indicators |
| **Status: Error** | `#7A2E2E` / `#A33D3D` | Muted Oxblood / Crimson banner & alerts |
| **Status: Pending** | `#C59B27` | Polished Brass / Warm Amber spinner & progress bar |

### 2.2 Typography & Editorial Geometry
- **Headings & Title Display:** Refined serif or editorial display font (e.g., *Cormorant Garamond*, *Playfair Display*, or *Instrument Serif* via Google Fonts).
- **Body & Data Grid:** Clean, highly legible sans-serif (e.g., *Inter*, *Plus Jakarta Sans*).
- **Technical Metrics & Page Numbers:** Monospace numerals (e.g., *JetBrains Mono*) for byte counts, processing times, and page numbers.
- **Component Geometry:** Crisp, structured corners (`rounded-sm` to `rounded-md`, `border-[1px]`), subtle warm drop shadows (`shadow-2xl shadow-black/60`), and hairline brass dividers.

### 2.3 Motion & Tactile Micro-Interactions (React Bits)
- **Dropzone Interaction:** Subtle warm gold glow outline on drag-over with gentle scale (`scale-[1.005]`).
- **Processing Progress Bar:** Smooth brass liquid fill animation with subtle shimmer highlight.
- **State Transitions:** Fluid fade-and-slide layout transitions (`framer-motion` or CSS cubic-bezier easing).
- **Tactile Buttons:** Subtle inward press effect (`active:scale-[0.98]`) with gold foil highlight border.
- **Clipboard Paste:** Support `Ctrl+V` anywhere in the workspace to ingest copied PDF files instantly.

---

## 3. High-Level System Architecture

```
pdf-to-docx-converter/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── convert.py       # POST /stream, POST /jobs, GET /jobs/{id}
│   │   │       │   ├── events.py        # GET /jobs/{id}/events (SSE stream)
│   │   │       │   ├── batch.py         # POST /batch, GET /batch/{id}/zip
│   │   │       │   └── health.py        # GET /health (System telemetry & status)
│   │   │       └── router.py            # API V1 router aggregation
│   │   ├── core/
│   │   │   ├── config.py                # Environment configs, size/page thresholds
│   │   │   ├── security.py              # Magic-byte check, PDF sanitizer, bomb guard
│   │   │   └── exceptions.py            # Custom HTTP & conversion exception handlers
│   │   ├── services/
│   │   │   ├── pdf_validator.py         # pypdf / PyMuPDF structural & password check
│   │   │   ├── converter_engine.py      # pdf2docx worker with page callbacks
│   │   │   ├── job_manager.py           # In-memory / background job state registry
│   │   │   └── storage.py               # Ephemeral temp manager + auto-cleaner
│   │   ├── schemas/
│   │   │   ├── conversion.py            # Request/Response Pydantic models
│   │   │   └── job.py                   # Job status, SSE payload, batch models
│   │   ├── utils/
│   │   │   └── filename.py              # RFC 5987 / 6266 Unicode filename encoder
│   │   └── main.py                      # FastAPI app entrypoint, CORS, GC lifecycle
│   ├── tests/
│   │   ├── test_validator.py            # Magic byte, password, corrupt file tests
│   │   ├── test_conversion.py           # Single-page, multi-page, table conversions
│   │   └── test_api.py                  # API endpoints and SSE stream integration tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── assets/                      # Icons, editorial badges, textures
│   │   ├── components/
│   │   │   ├── ui/                      # Custom Old Money shadcn/ui primitives
│   │   │   │   ├── button.jsx
│   │   │   │   ├── progress.jsx
│   │   │   │   ├── card.jsx
│   │   │   │   ├── badge.jsx
│   │   │   │   ├── dialog.jsx
│   │   │   │   ├── tabs.jsx
│   │   │   │   └── tooltip.jsx
│   │   │   ├── bits/                    # React Bits motion components
│   │   │   │   ├── ShimmerBorder.jsx
│   │   │   │   ├── SmoothReveal.jsx
│   │   │   │   └── NumberCounter.jsx
│   │   │   └── workspace/
│   │   │       ├── Dropzone.jsx         # Tactile file ingestion + clipboard paste
│   │   │       ├── FilePreviewCard.jsx  # PDF.js thumbnail, metadata & page range picker
│   │   │       ├── PasswordModal.jsx    # Locked PDF password prompt
│   │   │       ├── ConversionProgress.jsx # Real-time SSE stage & page tracker
│   │   │       ├── BatchQueue.jsx       # Multi-file queue table & ZIP downloader
│   │   │       ├── ResultCard.jsx       # Download action, metrics & reconvert CTA
│   │   │       └── ErrorBanner.jsx      # Desaturated Oxblood error display
│   │   ├── hooks/
│   │   │   ├── usePdfPreflight.js       # Client-side PDF.js thumbnail & page count
│   │   │   ├── useConversionJob.js      # SSE event listener & progress state machine
│   │   │   └── useBatchQueue.js         # Multi-file upload orchestrator
│   │   ├── services/
│   │   │   └── api.js                   # Axios client + SSE EventSource wrapper
│   │   ├── styles/
│   │   │   └── index.css                # Old Money typography, variables & Tailwind
│   │   ├── utils/
│   │   │   ├── fileHelpers.js           # File size formatting, extension check
│   │   │   └── download.js              # Blob URL generator & trigger
│   │   ├── App.jsx                      # Main workspace orchestrator
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 4. Detailed Module Specifications

### Module 1: Backend Core, Configuration & Ephemeral Storage
- **FastAPI Core (`backend/app/main.py`):**
  - Configured with strict CORS (whitelist frontend origin), custom OpenAPI docs tags, and structured JSON error responses.
  - Startup lifespan event: Initializes a background garbage collection loop (cleaning dangling `.pdf` and `.docx` files older than 15 mins).
- **Ephemeral Storage Manager (`backend/app/services/storage.py`):**
  - Creates dedicated isolated session directories in `tempfile.gettempdir() / "pdf2docx_sessions" / {session_id}`.
  - Registers `fastapi.BackgroundTasks` hooks on all download routes to unlink temp files immediately after response finishes streaming.
- **System Telemetry Probe (`GET /api/v1/health`):**
  - Returns service status, active conversion worker count, available disk space, and memory usage.

---

### Module 2: File Ingestion, Security Validator & Engine Worker
- **Security & Validator (`backend/app/services/pdf_validator.py`):**
  - **Magic Byte Verification:** Checks first 5 bytes for `%PDF-` to prevent disguised binary exploits.
  - **Decompression Bomb & Size Guard:** Rejects files exceeding `MAX_FILE_SIZE_MB` (default 50MB) or `MAX_PAGE_COUNT` (default 250 pages).
  - **Encryption Probe:** Inspects `is_encrypted`. If encrypted, validates whether provided password unlocks document using `pypdf` / `fitz`.
  - **Scanned Document Detection:** Heuristic check (analyzing glyph density across pages) to alert the user if the document is a pure raster image scan.
- **Isolated Conversion Engine (`backend/app/services/converter_engine.py`):**
  - Executes `pdf2docx.Converter` in a `concurrent.futures.ProcessPoolExecutor` with worker timeout watchdog (default 120s max).
  - Wraps conversion with page-by-page progress callback:
    ```python
    def convert_with_progress(pdf_path, docx_path, pages=None, progress_callback=None):
        cv = Converter(pdf_path)
        # Custom page range support (e.g. pages=[0, 1, 2] or full doc)
        cv.convert(docx_path, pages=pages)
        cv.close()
    ```
- **Job State Registry (`backend/app/services/job_manager.py`):**
  - Maintains job states (`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED`) with real-time page progress, percentage, and error logs in thread-safe storage.

---

### Module 3: REST & Real-Time SSE API Contracts
- **Endpoints:**
  1. `POST /api/v1/convert/stream`: Direct multipart upload for instant conversion & streaming download (ideal for single files < 10 pages).
  2. `POST /api/v1/convert/jobs`: Initiates async conversion job. Accepts `file`, optional `password`, and optional `page_range` (e.g. `"1-5, 8"`). Returns `{ job_id, status: "QUEUED", total_pages }`.
  3. `GET /api/v1/jobs/{job_id}/events`: Server-Sent Events (SSE) stream emitting real-time progress events:
     ```json
     event: progress
     data: {"job_id": "...", "stage": "CONVERTING", "current_page": 6, "total_pages": 18, "percent": 33}
     ```
  4. `GET /api/v1/jobs/{job_id}/download`: Streams final `.docx` binary with correct `Content-Disposition: attachment; filename*=UTF-8''...` headers.
  5. `POST /api/v1/batch`: Ingests multiple files, creates a batch job, and provides `GET /api/v1/batch/{batch_id}/zip` to bundle all converted Word docs into a single ZIP.

---

### Module 4: Frontend "Old Money" Design System & PDF Preflight
- **Design Tokens & Tailwind Configuration:**
  - Full palette integration in `tailwind.config.js` and `src/styles/index.css`.
  - Bespoke serif typography imported via Google Fonts (*Cormorant Garamond* / *Instrument Serif*).
- **Client-Side PDF Preflight Hook (`usePdfPreflight.js`):**
  - Uses `pdfjs-dist` in a lightweight web worker to parse dropped PDFs:
    - Extracts total page count.
    - Generates high-DPI canvas thumbnail of page 1.
    - Detects whether file is password protected before upload.
- **Customized UI Primitives:**
  - Tactile gold-bordered cards, muted brass pill badges, and editorial tabs.
  - Rich micro-interactions: Smooth progress bars, glowing gold focus rings, tactile button presses.

---

### Module 5: Interactive Workspace & User Experience
- **1. Ingestion State:**
  - Dropzone with tactile hairline border and subtle gold hover glow.
  - Supports Drag-and-Drop, File Browser, and **Direct Clipboard Paste (`Ctrl+V`)**.
- **2. Preflight & Configuration Card:**
  - Displays rendered page 1 thumbnail, file name, file size, and page count badge.
  - Optional **Page Range Selector** (Convert All Pages vs Custom Range like `1-3, 5`).
  - Password Input prompt if encrypted.
- **3. Conversion Tracker (Live SSE Feedback):**
  - Dynamic 4-step progress stepper:
    - `[1] File Upload` -> `[2] Structure Parsing` -> `[3] Page Reconstruction (X/Y)` -> `[4] Document Packaging`.
  - Real-time animated brass progress bar and percentage counter.
- **4. Completed State:**
  - Instant auto-download or manual "Download Word Document (.docx)" button.
  - Conversion summary metrics: Conversion duration (e.g. `2.4s`), output file size, and "Convert Another" CTA.
- **5. Batch Mode:**
  - Multi-file queue table with individual file status bars, cancel buttons, and global "Download All (ZIP)" CTA.
- **6. Error State:**
  - Desaturated Oxblood alert banner with clear human-readable explanations (e.g. "Password incorrect", "Corrupt PDF structure", "Exceeded 50MB limit").

---

### Module 6: Resilience, Security, Containerization & CI/CD
- **Memory & Resource Caps:**
  - `ProcessPoolExecutor(max_workers=4)` prevents server RAM crashes during concurrent multi-page conversions.
  - Per-job conversion timeout (120s) forcibly terminates stalled worker processes.
- **Multi-Stage Containerization:**
  - **Backend Dockerfile:** Python 3.11-slim with pre-installed system dependencies (`libgl1`, `libmupdf-dev`, `gcc`), running as a non-root user (`appuser`).
  - **Frontend Dockerfile:** Multi-stage build (Node 20 build -> Nginx Alpine serving static assets with gzip and security headers).
  - **Root `docker-compose.yml`:** Single-command local startup (`docker compose up --build`) orchestrating backend on port 8000 and frontend on port 3000.

---

### Module 7: Quality Assurance & Testing Suite
- **Backend Tests (`pytest`):**
  - `test_validator.py`: Tests valid PDFs, zero-byte files, non-PDF disguised binaries, password-locked PDFs, oversized PDFs.
  - `test_converter.py`: Tests single-page, multi-page, multi-column layout, and tables preservation.
  - `test_api.py`: Tests `/convert/stream`, `/convert/jobs`, `/jobs/{id}/events` SSE stream, and `/health`.
- **Frontend Tests (`vitest` + React Testing Library):**
  - Tests dropzone drag-and-drop ingestion, clipboard paste handler, preflight thumbnail generation, and progress state transitions.

---

## 5. Step-by-Step Implementation Roadmap

| Phase | Tasks & Deliverables | Verification Milestone |
| :--- | :--- | :--- |
| **Phase 1** | Backend foundational setup: FastAPI app, configuration, CORS, ephemeral session storage, and health endpoint. | `GET /api/v1/health` returns 200 with system telemetry. |
| **Phase 2** | Security validator & conversion worker: Magic bytes, password checking, `pdf2docx` worker in `ProcessPoolExecutor`, page progress callbacks. | Pytest suite passes for PDF validation and layout conversion. |
| **Phase 3** | API Endpoints: Direct stream (`/convert/stream`), Async jobs (`/convert/jobs`), and SSE real-time stream (`/jobs/{id}/events`). | Test converting a sample PDF via Curl / Postman receiving live SSE events. |
| **Phase 4** | Frontend scaffolding: Vite + React, Tailwind Old Money theme tokens, typography, shadcn/ui primitives, and React Bits components. | UI renders Old Money color scheme and tactile styling accurately. |
| **Phase 5** | PDF Preflight & Workspace Components: `pdfjs-dist` thumbnail extraction, Dropzone (`Ctrl+V` paste support), Page range picker, Password modal. | Dropping a PDF instantly displays thumbnail and page count without upload. |
| **Phase 6** | Conversion Monitor & End-to-End Flow: SSE connection hook, real-time progress bar, result card, and automatic DOCX download trigger. | Full end-to-end PDF -> DOCX conversion runs with live progress and download. |
| **Phase 7** | Batch Processing & Error Resilience: Multi-file queue table, ZIP packaging, and Oxblood error handling. | Batch upload converts 3 PDFs concurrently and downloads a ZIP. |
| **Phase 8** | Docker containerization & documentation: Multi-stage Dockerfiles, `docker-compose.yml`, and comprehensive root `README.md`. | `docker compose up` spins up fully functional frontend & backend. |