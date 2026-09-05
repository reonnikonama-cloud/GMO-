# ==========================================
# Stage 1: Rust Builder (フルイメージを使用)
# ==========================================
FROM rust:1.76 as rust-builder

WORKDIR /usr/src/app

# Pythonビルド用のヘッダーのみインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir maturin

COPY Cargo.toml Cargo.lock* pyproject.toml* ./
COPY rust_src ./rust_src

# ビルド実行
RUN maturin build --release --out dist
