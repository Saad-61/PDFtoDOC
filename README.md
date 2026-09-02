# PDF to DOCX — Editorial Document Reconstructor

A high-performance, layout-preserving **PDF to Word DOCX converter** built with **Python (FastAPI)** and **React (Vite)**. Styled with an understated **"Old Money" dark editorial visual identity**, the system emphasizes privacy-first ephemeral storage, real-time Server-Sent Events (SSE) progress tracking, and precision layout reconstruction.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend (React + Vite)"]
        A[User Drops PDF / Ctrl+V] --> B[PDF.js Client-Side Preflight]
        B -->|Extract Page Count & Thumbnail| C[Preflight Review & Page Scope]
        C -->|Instant Stream| D[Direct POST /api/v1/convert/stream]
        C -->|Async Job Path| E[POST /api/v1/convert/jobs]
        E --> F[EventSource SSE Listener: /jobs/{id}/events]
        F -->|Real-time Stepper| G[Reconstructing Page X of Y]
        G -->|Completed| H[Automatic DOCX Download Trigger]
    end

    subgraph Server ["Backend (FastAPI + PyMuPDF + pdf2docx)"]
        D --> I[Ephemeral Storage: Session Directory]
        E --> I
        I --> J[PDF Security & Magic Header Validator]
        J --> K[Password Decryption Engine]
        K --> L[Layout Engine Worker Pool]
        L -->|Per-Page Callbacks| M[JobManager SSE Pub/Sub]
        M --> F
        L --> N[Generate .docx OpenXML Document]
        N --> O[Ephemeral Auto-Cleanup Hook]
    end
```

---

## 2. Key Architectural Features

- **Dual Conversion Pipeline:**
  - **Fast Stream Path (`POST /api/v1/convert/stream`):** Instant synchronous streaming download for small documents (< 10 pages).
  - **Asynchronous SSE Job Path (`POST /api/v1/convert/jobs`):** Spawns an isolated background worker publishing real-time per-page layout reconstruction progress over Server-Sent Events (`text/event-stream`).
- **Client-Side Preflight (`pdfjs-dist`):** Renders high-DPI page 1 thumbnail canvas, extracts page counts, and detects password locks in the browser before network transmission.
- **Selective Page Extraction:** Supports custom extraction ranges (e.g. `1-3, 5, 8-10`) alongside full document conversion.
- **Password-Protected PDF Support:** Detects encrypted PDFs and provides an inline unlocking dialog.
- **Zero-Trace Ephemeral Lifecycle:** Guaranteed automatic cleanup via FastAPI `BackgroundTasks` upon file delivery, plus a periodic background garbage collection daemon pruning any files older than 15 minutes.
- **International Filename Support:** Uses RFC 5987 / RFC 6266 `Content-Disposition: attachment; filename*=UTF-8''...` to preserve accented and non-Latin character sets.
- **Multi-Document Batch Processing:** Multi-file drag-and-drop queue with concurrent status tracking and single-click batch downloads.

---

## 3. Visual Identity: "Old Money" Design System

The application strictly avoids generic modern SaaS tropes (no translucent glassmorphism, no neon cyan/magenta gradients, no bubbly oversized curves).

| Token | Hex Code | Role |
| :--- | :--- | :--- |
| **Base Background** | `#121316` | Deep Matte Carbon primary canvas |
| **Surfaces** | `#1A1B1F` / `#222328` | Layered dark charcoal workspace cards |
| **Hairline Borders** | `#2E2F35` | Slate-bronze 1px structured borders |
| **Primary Accent** | `#C5A059` / `#D4AF37` | Warm Antique Gold / Champagne Gold |
| **Typography** | `#F5F4F0` / `#A8A69E` | Soft Ivory headings & Warm Taupe metadata |
| **Status (Success)** | `#2D5A43` | Deep English Forest Green |
| **Status (Error)** | `#7A2E2E` | Muted Oxblood / Crimson |

**Typography Pairing:** *Cormorant Garamond* (Google Fonts display serif) paired with *Inter* for body text and *JetBrains Mono* for technical metrics.

---

## 4. Quick Start with Docker Compose

Run the entire containerized stack with a single command:

```bash
docker compose up --build
```

- **Frontend Application:** Access at [http://localhost:3000](http://localhost:3000)
- **Backend API & OpenAPI Docs:** Access at [http://localhost:8000/docs](http://localhost:8000/docs)
- **Telemetry Probe:** Access at [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 5. Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run automated test suite
pytest -c pytest.ini -v

# 5. Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Launch Vite development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 6. API Specification Reference

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint | Description | Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Live host telemetry & memory metrics | None | `200 OK` (JSON metrics) |
| `POST` | `/convert/validate` | PDF preflight inspection | `multipart/form-data` (`file`, optional `password`) | `200 OK` (`ValidationResult`) |
| `POST` | `/convert/stream` | Synchronous direct stream conversion | `multipart/form-data` (`file`, optional `page_range`, `password`) | `200 OK` (DOCX binary attachment) |
| `POST` | `/convert/jobs` | Enqueue async conversion job | `multipart/form-data` (`file`, optional `page_range`, `password`) | `202 Accepted` (`JobCreateResponse`) |
| `GET` | `/jobs/{id}` | Job status & progress polling | None | `200 OK` (`JobProgressResponse`) |
| `GET` | `/jobs/{id}/events` | Real-time Server-Sent Events stream | None | `text/event-stream` |
| `GET` | `/jobs/{id}/download`| Download completed DOCX binary | None | `200 OK` (DOCX binary attachment) |

---

## 7. Environment Variables

Configure via `.env` file in `backend/`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Whitelisted client origins |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload size threshold |
| `MAX_PAGE_COUNT` | `250` | Maximum allowable document pages |
| `CONVERSION_TIMEOUT_SECONDS` | `120` | Watchdog timeout for conversion workers |
| `SESSION_EXPIRY_MINUTES` | `15` | Retention window before garbage collector sweeps temp files |

---

## 8. Quality Assurance & Testing

Run all 22 backend automated unit and integration tests:

```bash
backend/.venv/Scripts/pytest.exe -c backend/pytest.ini -v
```

Build the production frontend bundle:

```bash
cd frontend && npm run build
```

---

## 9. License & Security

- **Zero Server Retention:** Uploaded files and generated documents are ephemeral and automatically unlinked after transmission.
- **Protected Environment:** Sensitive documents (such as user resumes and password files) are strictly excluded from version control via `.gitignore`.
