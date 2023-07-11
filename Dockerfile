FROM python:3.11-slim-buster
RUN apt-get update
RUN apt-get install nano

RUN mkdir wd
WORKDIR wd
COPY kami_reports/requirements.txt .
RUN pip install -r requirements.txt
 
COPY kami_reports/ ./
 
CMD [ "gunicorn", "--workers=5", "--threads=1", "--preload", "-b 0.0.0.0:80", "app:server"]