FROM docker.io/python:3.10-slim

ADD ./requirements.txt /tmp/requirements.txt

RUN apt update && \
    apt install -y \
        gcc \
    && \
    pip install --no-cache-dir \
        -r /tmp/requirements.txt \
    && \
    apt remove -y \
        gcc \
    && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace