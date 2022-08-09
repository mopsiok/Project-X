FROM python:3.9-slim

COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt


ENV PYTHONUNBUFFERED 1