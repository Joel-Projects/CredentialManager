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

RUN addgroup --system app && \
    adduser --system --group app

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common bash cron nano netcat
#    add-apt-repository ppa:certbot/certbot && \

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

#COPY ./entrypoint.sh $APP_HOME/entrypoint.sh
COPY ./app $APP_HOME/app
COPY ./config.py $APP_HOME/config.py
COPY ./gunicorn.conf.py $APP_HOME/gunicorn.conf.py
COPY ./flask_restplus_patched $APP_HOME/flask_restplus_patched
#COPY ./credmgr.jesassn.org.conf /etc/nginx/sites-enabled/credmgr

RUN #mkdir /var/lib/letsencrypt /var/log/letsencrypt

RUN chown -R app:app $APP_HOME
#    chown -R letsencrypt:letsencrypt /etc/letsencrypt /var/lib/letsencrypt /var/log/letsencrypt && \
#    chmod +x $APP_HOME/entrypoint.sh

EXPOSE 5000
#VOLUME /etc/letsencrypt

#ENTRYPOINT ["/home/app/credmgr/entrypoint.sh"]
RUN ["gunicorn"]