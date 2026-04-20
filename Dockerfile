FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY computor_v2/ ./computor_v2/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["uv", "run", "python", "-m", "computor_v2.main"]