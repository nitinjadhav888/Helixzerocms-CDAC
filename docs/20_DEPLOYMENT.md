# 20. DEPLOYMENT & PRODUCTION INFRASTRUCTURE
## Containerization, Environment Configuration, and HPC Deployment
**Status:** `VERIFIED — CURRENT IMPLEMENTATION`  

---

### 1. Deployment Topologies

HelixZero supports three primary deployment configurations:

1. **Local Workstation / Laboratory Terminal:**
   - Platform: Microsoft Windows 11 / Linux.
   - Execution: Native Python 3.11 virtual environment via `start_system.bat` or `uvicorn api.main:app --port 8000`.
   - Latency: Direct memory-mapped access to models and caches ($< 0.1$ s per scan).

2. **Containerized Microservice (Docker):**
   - Base Image: `python:3.11-slim` (Debian Bookworm).
   - Port Binding: Container port `8000` mapped to host.
   - Resource Allocation: 2–4 CPU cores, 4–8 GB RAM.

3. **High-Performance Computing Cluster (C-DAC PARAM / HPC):**
   - High-throughput batch job arrays submitted via SLURM scheduler to screen full transcriptomes or million-compound chemical libraries.

---

### 2. Dockerfile Walkthrough

From `Dockerfile`:
```dockerfile
# ── Stage 1: Base Environment ──
FROM python:3.11-slim

# System dependencies for compilation and curl probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY smepred/ ./smepred/
COPY final_benchmarks/ ./final_benchmarks/
COPY helixzero/ ./helixzero/

# Expose microservice port
EXPOSE 8000

# Docker healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch production ASGI server
WORKDIR /app/smepred
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3. Environment Variables & Configuration

Configurable via `.env` or system environment:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port on which Uvicorn listens for incoming HTTP traffic. |
| `HOST` | `0.0.0.0` | Host interface binding (`0.0.0.0` for all external interfaces). |
| `GEMINI_API_KEY` | Optional | API key for Google Gemini conversational assistant co-pilot. |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

### 4. Health Checks and Production Monitoring

- **Liveness & Readiness Probe:** `GET /health` returns HTTP 200 with payload:
  `{"status": "ok", "version": "2.1.0", "service": "HelixZero-CMS"}`
- **Memory Management:** The 863.8 MB transcriptome binary index is lazy-loaded upon first demand, keeping the idle startup memory footprint below 350 MB.

---

### 5. Git LFS Binary Integrity & Container Initialization

- **Binary Checkpoints & Calibrators:** The production runtime relies on native model binaries and pickled calibrators located in `smepred/models/` (`model_normal.txt`, `unified_dose_catboost.cbm`, `calibrator_naked.pkl`, `calibrator_context.pkl`).
- **Git LFS Requirement:** In containerized or cloned environments, execute `git lfs pull` before building or launching the container to ensure that files like `calibrator_naked.pkl` are real binary artifacts (2.2 KB) rather than 118-byte Git LFS pointer stubs.
- **Port Standardization:** Both Docker container configurations and local development scripts standardize on port `8000` (`http://0.0.0.0:8000`), aligned with the frontend API Gateway configuration.

