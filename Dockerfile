FROM python:3.7-alpine

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED 1