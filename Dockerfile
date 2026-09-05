# ==========================================
# Stage 1: Rust Builder
# ==========================================
FROM rust:1.76-slim as rust-builder

WORKDIR /usr/src/app

# SSL証明書の更新と必須ツールのインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    ca-certificates \
    git \
    pkg-config \
    libssl-dev \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Cargo内部通信エラーを回避する環境変数設定
ENV CARGO_NET_GIT_FETCH_WITH_CLI=true
ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir maturin

COPY Cargo.toml Cargo.lock* pyproject.toml* ./
COPY rust_src ./rust_src

# 依存パッケージの事前フェッチとビルド
RUN cargo fetch
RUN maturin build --release --out dist
