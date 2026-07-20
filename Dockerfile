FROM python:3.14-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1

WORKDIR /muzbot

COPY uv.lock pyproject.toml .python-version ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \ 
    uv sync --frozen --all-packages --no-editable --no-dev


FROM python:3.14-alpine AS runner
ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache ffmpeg && \
    apk cache clean && \
    rm -rf /var/cache/apk/*
    
WORKDIR /muzbot
COPY --from=builder /muzbot/.venv/ .venv/
COPY . .
ENV PATH="/muzbot/.venv/bin:$PATH"
CMD ["python", "main.py"]
