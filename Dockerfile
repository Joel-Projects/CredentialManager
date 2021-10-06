FROM python:3.9-slim-buster as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app/requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt pip

FROM python:3.9-slim-buster

ENV HOME=/home/app
ENV APP_HOME=$HOME/credmgr
ENV FLASK_CONFIG production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ America/Chicago

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends bash nano

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

COPY ./app $APP_HOME/app
COPY ./config.py $APP_HOME/config.py
COPY ./gunicorn.conf.py $APP_HOME/gunicorn.conf.py
COPY ./flask_restplus_patched $APP_HOME/flask_restplus_patched

EXPOSE 5000

CMD ["gunicorn"]
