#!/usr/bin/env bash
set -e

echo "=== Trading Bot プロジェクト構造を作成中 ==="

# 1. ディレクトリ群の作成
mkdir -p trader/common
mkdir -p trader/scalping/rust_src/src
mkdir -p trader/daytrading
mkdir -p trader/swing
mkdir -p trader/position

# 2. requirements.txt の作成
cat << 'EOF' > requirements.txt
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
maturin>=1.0.0
EOF

# 3. Dockerfile の作成 (Rust + Python マルチステージビルド)
cat << 'EOF' > Dockerfile
FROM rust:1.75-slim as rust-builder
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y python3-dev python3-pip python3-venv

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install maturin

COPY trader/scalping/rust_src /usr/src/app/rust_src
WORKDIR /usr/src/app/rust_src
RUN maturin build --release -o /usr/src/app/wheels

FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=rust-builder /opt/venv /opt/venv
COPY --from=rust-builder /usr/src/app/wheels /tmp/wheels
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install /tmp/wheels/*.whl || true

COPY . .

EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
EOF

# 4. render.yaml の作成 (Render Blueprint 設定)
cat << 'EOF' > render.yaml
services:
  - type: web
    name: trading-bot-service
    env: docker
    plan: free
    region: singapore
    envVars:
      - key: PORT
        value: 10000
EOF

# 5. main.py の作成 (Render用ヘルスチェック + FastAPI)
cat << 'EOF' > main.py
import os
import asyncio
from fastapi import FastAPI

app = FastAPI(title="Trading Bot Service")

@app.get("/")
def health_check():
    """Render ヘルスチェック用エンドポイント"""
    return {"status": "ok", "service": "Trading Bot Manager"}

@app.on_event("startup")
async def startup_event():
    """サービス起動時のトレード監視バックグラウンドタスク"""
    asyncio.create_task(run_trading_loop())

async def run_trading_loop():
    print("=== Trading Bot Loop Started ===")
    while True:
        await asyncio.sleep(10)
EOF

# 6. Rust 側の最小プロジェクト設定 (Cargo.toml & lib.rs)
cat << 'EOF' > trader/scalping/rust_src/Cargo.toml
[package]
name = "rust_scalp_engine"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_scalp_engine"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20.0", features = ["extension-module"] }
serde = { version = "1.0", features = ["derive"] }
EOF

cat << 'EOF' > trader/scalping/rust_src/src/lib.rs
use pyo3::prelude::*;

#[pyfunction]
fn ping() -> PyResult<String> {
    Ok("Rust Scalp Engine Active".to_string())
}

#[pymodule]
fn rust_scalp_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    Ok(())
}
EOF

# 7. __init__.py 群およびモジュール雛形の作成
touch trader/__init__.py
touch trader/common/__init__.py
touch trader/scalping/__init__.py
touch trader/daytrading/__init__.py
touch trader/swing/__init__.py
touch trader/position/__init__.py

echo "=== 作成完了 ==="
