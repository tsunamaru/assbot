FROM docker.io/python:3.11-slim

ADD ./requirements.txt /tmp/requirements.txt

RUN apt update && \
    apt install -y \
        gcc \
        locales \
    && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="en_US.UTF-8"' > /etc/default/locale && \
    dpkg-reconfigure -f noninteractive locales && \
    update-locale LANG=en_US.UTF-8 && \
    pip install --no-cache-dir \
        -r /tmp/requirements.txt \
    && \
    apt remove -y \
        gcc \
    && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

WORKDIR /workspace