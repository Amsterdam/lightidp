FROM python:3.6-slim

EXPOSE 8000

RUN adduser --system datapunt

WORKDIR /app
COPY . /app/
RUN apt-get update \
    && apt-get install -y build-essential \
    && pip install --no-cache-dir .

USER datapunt

CMD uwsgi --need-app
