FROM python:3.9-slim as builder
LABEL maintainer="maicon@kamico.com.br"

RUN pip install poetry
RUN mkdir -p /app
COPY . /app

WORKDIR /app
RUN poetry install --without dev

FROM python:3.9-slim as base
COPY --from=builder /app /app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8081
ENTRYPOINT ["python", "app/app_t.py"]