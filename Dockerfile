FROM python:3.10
ENV TZ="America/Sao_Paulo"
RUN pip install poetry

WORKDIR /app
COPY . /app
RUN poetry install
CMD ["poetry", "run", "python", "service.py"]