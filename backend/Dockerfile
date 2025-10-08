# Multi-stage build: frontend -> backend runtime

# Stage 1: Frontend build
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
	ca-certificates build-essential curl && \
	update-ca-certificates && \
	pip install --upgrade pip && \
	pip install --no-cache-dir --retries 5 --timeout 60 -r requirements.txt && \
	useradd -m appuser && \
	rm -rf /var/lib/apt/lists/*
COPY backend/app ./app
# Copy built frontend (React creates build/)
COPY --from=frontend-build /frontend/build ./app/static
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
