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
