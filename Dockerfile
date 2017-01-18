FROM python:3.6
MAINTAINER datapunt.ois@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN apt-get update \
    && adduser --system datapunt

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt
COPY . /app/
