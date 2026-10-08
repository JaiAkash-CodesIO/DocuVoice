# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with Tesseract OCR engine
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Install native system dependencies for OpenCV, PyMuPDF, and Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create Hugging Face Spaces non-root user (UID 1000)
RUN useradd -m -u 1000 user
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, sample documents, and compiled React frontend
COPY backend ./backend
COPY samples ./samples
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set permissions for upload storage directories
RUN mkdir -p uploads processed && chown -R user:user /app

USER user

EXPOSE 7860

# Start unified FastAPI server serving both API & UI on port 7860
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
