FROM ghcr.io/tsunamaru/assbot/base:latest

ADD main.py .
ADD cfg.py .

USER nobody

CMD ["python", "main.py"]