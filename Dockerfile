FROM python:3.10-slim
ENV TZ="America/Sao_Paulo"

WORKDIR /app
COPY pyproject.toml service.py README.md /app/
COPY kami_reports /app/kami_reports/
RUN pip install poetry && \
    poetry install --no-dev

CMD ["poetry", "run", "python", "service.py"]