FROM python:3.11-slim-buster
FROM python:3.10
ENV TZ="America/Sao_Paulo"
RUN apt-get update
RUN apt-get install nano
RUN pip install poetry
WORKDIR /app
COPY . /app
RUN poetry install
 
COPY kami_reports/ ./
 
CMD ["poetry", "run", "gunicorn", "--workers=5", "--threads=1", "--preload", "-b 0.0.0.0:8090", "app:server"]