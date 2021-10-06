FROM python:3.9-slim-buster as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app/requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt pip

FROM python:3.9-slim-buster

ENV FLASK_CONFIG production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ America/Chicago

RUN mkdir -p /home/app/credmgr
WORKDIR /home/app/credmgr

RUN apt-get update && \
    apt-get install -y --no-install-recommends bash nano

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

COPY ./app /home/app/credmgr/app
COPY ./config.py /home/app/credmgr/config.py
COPY ./gunicorn.conf.py /home/app/credmgr/gunicorn.conf.py
COPY ./flask_restplus_patched /home/app/credmgr/flask_restplus_patched

EXPOSE 5000

CMD ["gunicorn"]
