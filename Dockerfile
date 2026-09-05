# ==========================================
# Stage 1: Rust Builder
# ==========================================
FROM rust:latest AS rust-builder

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=git
ENV CARGO_NET_GIT_FETCH_WITH_CLI=true

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir maturin

COPY Cargo.toml Cargo.lock* pyproject.toml ./
COPY rust_src ./src

RUN maturin build --release --out dist

# ==========================================
# Stage 2: Python Runtime
# ==========================================
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=rust-builder /usr/src/app/dist ./dist
RUN pip install --no-cache-dir ./dist/*.whl && rm -rf ./dist

COPY . .

EXPOSE 10000

CMD ["uvicorn", "trader.main:app", "--host", "0.0.0.0", "--port", "10000"]
