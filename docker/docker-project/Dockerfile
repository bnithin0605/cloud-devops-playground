FROM python:3.9-slim

WORKDIR /home/data

COPY IF.txt /home/data/
COPY AlwaysRememberUsThisWay.txt /home/data/
COPY script.py /home/data/

RUN mkdir -p /home/data/output

CMD ["python", "script.py"]