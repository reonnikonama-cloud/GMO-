# ==========================================
# Stage 1: Rust Builder
# ==========================================
FROM rust:1.76-slim as rust-builder

WORKDIR /usr/src/app

# Cコンパイルに必要な python3-dev を追加
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir maturin

# 設定ファイル群をコピー（Cargo.lock / pyproject.toml の読み込みを保証）
COPY Cargo.toml Cargo.lock* pyproject.toml* ./
COPY rust_src ./rust_src

# BuildKit キャッシュを利用してクレート再コンパイルを回避・高速化
RUN --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/usr/src/app/target \
    maturin build --release --out dist

# ==========================================
# Stage 2: Python Runtime
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# 実行環境に不要な build-essential は除外して軽量化
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ディレクトリごとコピーして確実にインストール後、一時ファイルを削除
COPY --from=rust-builder /usr/src/app/dist ./dist
RUN pip install --no-cache-dir ./dist/*.whl && rm -rf ./dist

COPY . .

EXPOSE 10000

CMD ["uvicorn", "trader.main:app", "--host", "0.0.0.0", "--port", "10000"]
