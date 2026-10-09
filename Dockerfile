# =============================================================================
# HelixZero-CMS — Production Docker Container
# Docker Hub: nitinjadhav888/helixzerocms:latest
# =============================================================================

# Stage 0: Asset carrier for large binary models and 863MB transcriptome index
FROM nitinjadhav888/helixzerocms:latest AS prebuilt_assets

# Stage 1: Main production container
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
# Large Data Assets & Model Embeddings
# (Extracted from prebuilt image so CI/CD does not require 1GB+ files in Git)
# ---------------------------------------------------------------------------
COPY --from=prebuilt_assets /app/smepred/data/human_transcriptome.idx.pkl /app/smepred/data/human_transcriptome.idx.pkl
COPY --from=prebuilt_assets /app/data_pre/ /app/data_pre/
COPY --from=prebuilt_assets /app/MEG-mod-main/Saved_Best_Models/ /app/MEG-mod-main/Saved_Best_Models/
COPY --from=prebuilt_assets /app/smepred/models/ /app/smepred/models/

# ---------------------------------------------------------------------------
# Copy Fresh Application Code & Data
# (Overwrites model binaries with latest Git-tracked versions)
# ---------------------------------------------------------------------------
COPY smepred/ /app/smepred/
COPY helixzero/ /app/helixzero/
COPY helixzero_ieee_v5/ /app/helixzero_ieee_v5/
COPY MEG-mod-main/ /app/MEG-mod-main/

# ---------------------------------------------------------------------------
# Build-time verification: confirms idx.pkl (>800MB) & rnafm (>50MB) & cbm (>1MB)
# ---------------------------------------------------------------------------
RUN python3 -c "\
import os, sys; \
idx_path = '/app/smepred/data/human_transcriptome.idx.pkl'; \
idx_size = os.path.getsize(idx_path); \
assert idx_size > 800_000_000, f'idx.pkl too small or corrupt: {idx_size} bytes!'; \
fm_path = '/app/smepred/models/rnafm_embeddings.pkl'; \
fm_size = os.path.getsize(fm_path) if os.path.exists(fm_path) else 0; \
assert fm_size > 50_000_000, f'CRITICAL: rnafm_embeddings.pkl too small or LFS stub: {fm_size} bytes!'; \
cbm_path = '/app/smepred/models/unified_dose_catboost.cbm'; \
cbm_size = os.path.getsize(cbm_path) if os.path.exists(cbm_path) else 0; \
assert cbm_size > 1_000_000, f'CRITICAL: unified_dose_catboost.cbm missing or corrupt: {cbm_size} bytes!'; \
print(f'[BUILD VERIFY] idx.pkl: {idx_size/1e6:.0f} MB | rnafm: {fm_size/1e6:.1f} MB | cbm: {cbm_size/1e6:.2f} MB confirmed in image.'); \
sys.exit(0)"

# ---------------------------------------------------------------------------
# Set Python Path so all module imports resolve correctly
# ---------------------------------------------------------------------------
ENV PYTHONPATH="/app:/app/smepred:/app/helixzero:/app/MEG-mod-main"
ENV PYTHONUNBUFFERED=1

# Expose port 8000 (Uvicorn)
EXPOSE 8000

# Healthcheck — FastAPI responds at /health with {"status": "ok"}
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn FastAPI server (no --reload in production)
CMD ["uvicorn", "smepred.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--timeout-keep-alive", "300"]
