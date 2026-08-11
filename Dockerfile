# =============================================================================
# HelixZero-CMS — Production Docker Container
# Docker Hub: nitinjadhav888/helixzerocms:latest
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# libgomp1   = required for LightGBM OpenMP multi-threading
# curl       = health checks
# gcc g++    = required for some Cython/C-extension packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first (lightweight ~200MB instead of 2.5GB CUDA build)
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install all Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Copy Application Code
# ---------------------------------------------------------------------------
COPY smepred/ /app/smepred/
COPY helixzero_ieee_v5/ /app/helixzero_ieee_v5/
COPY MEG-mod-main/ /app/MEG-mod-main/

# ---------------------------------------------------------------------------
# Copy Essential Data Files
# ---------------------------------------------------------------------------
COPY data_pre/cofold_results.pkl /app/data_pre/cofold_results.pkl
COPY data_pre/unimol_1b_emb_dict.pkl /app/data_pre/unimol_1b_emb_dict.pkl

# ---------------------------------------------------------------------------
# CRITICAL: Explicitly copy the pre-built transcriptome index (863MB).
# This is separate from the smepred/ COPY above to make it crystal clear
# this file MUST be in the image. The raw FASTA (449MB) is excluded via
# .dockerignore — this idx.pkl replaces it for instant O(1) off-target lookup.
# If this file is missing the RUN below will FAIL THE BUILD immediately.
# ---------------------------------------------------------------------------
COPY smepred/data/human_transcriptome.idx.pkl /app/smepred/data/human_transcriptome.idx.pkl

# Build-time verification: fails the build instantly if idx.pkl is missing or truncated.
# File-size check (must be > 800MB) is instant — avoids 3+ minute pickle.load deserialization.
RUN python3 -c "\
import os, sys; \
path = '/app/smepred/data/human_transcriptome.idx.pkl'; \
size = os.path.getsize(path); \
assert size > 800_000_000, f'idx.pkl too small or corrupt: {size} bytes!'; \
print(f'[BUILD VERIFY] idx.pkl OK: {size/1e6:.0f} MB confirmed in image.'); \
sys.exit(0)"

# ---------------------------------------------------------------------------
# Set Python Path so all module imports resolve correctly
# ---------------------------------------------------------------------------
ENV PYTHONPATH="/app:/app/smepred:/app/MEG-mod-main"
ENV PYTHONUNBUFFERED=1

# Expose port 8000 (Uvicorn)
EXPOSE 8000

# Healthcheck — FastAPI responds at /health with {"status": "ok"}
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn FastAPI server (no --reload in production)
CMD ["uvicorn", "smepred.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--timeout-keep-alive", "30"]
