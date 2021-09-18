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
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ America/Chicago

RUN addgroup --system letsencrypt && \
    addgroup --system app && \
    adduser --system --home /etc/letsencrypt --group letsencrypt && \
    adduser --system --group app

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y --no-install-recommends bash certbot cron gosu nano netcat python3-certbot-dns-cloudflare

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

COPY ./entrypoint.sh $APP_HOME/entrypoint.sh
COPY ./app $APP_HOME/app
COPY ./config.py $APP_HOME/config.py
COPY ./gunicorn.conf.py $APP_HOME/gunicorn.conf.py
COPY ./flask_restplus_patched $APP_HOME/flask_restplus_patched

RUN mkdir /var/lib/letsencrypt /var/log/letsencrypt

RUN chown -R app:app $APP_HOME && \
    chown -R letsencrypt:letsencrypt /etc/letsencrypt /var/lib/letsencrypt /var/log/letsencrypt && \
    chmod +x $APP_HOME/entrypoint.sh

EXPOSE 443 2222
VOLUME /etc/letsencrypt

ENTRYPOINT ["/home/app/credmgr/entrypoint.sh"]
