FROM rust:1.76-slim as rust-builder
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir maturin
COPY Cargo.toml ./
COPY rust_src ./rust_src
RUN maturin build --release --out dist

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=rust-builder /usr/src/app/dist/*.whl ./
RUN pip install --no-cache-dir *.whl && rm *.whl
COPY . .
EXPOSE 10000
CMD ["uvicorn", "trader.main:app", "--host", "0.0.0.0", "--port", "10000"]
