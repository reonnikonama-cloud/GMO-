# ==========================================
# Stage 1: Rust Builder
# ==========================================
FROM rust:1.76-slim as rust-builder

WORKDIR /usr/src/app

# SSL証明書(ca-certificates), git, Cライブラリ用ツールを追加
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    ca-certificates \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Cargoの依存取得を高速・安定化する通信設定
ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir maturin

COPY Cargo.toml Cargo.lock* pyproject.toml* ./
COPY rust_src ./rust_src

# 壊れたキャッシュの再利用を防ぐためシンプルなコマンドで実行
RUN maturin build --release --out dist
