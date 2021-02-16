FROM python:3.8-alpine3.8

COPY ./app /opt/www/CredentialManager/app
COPY ./config.py /opt/www/CredentialManager/config.py
COPY ./flask_restplus_patched /opt/www/CredentialManager/flask_restplus_patched

WORKDIR /opt/www/CredentialManager/app

ENV TZ America/Chicago
ENV FLASK_CONFIG production

RUN apk add --no-cache postgresql-libs nano bash && \
    apk add --no-cache --virtual alpine-sdk .build-deps make gcc python-dev libffi-dev musl-dev postgresql-dev&& \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

WORKDIR /opt/www/CredentialManager/

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "-k", "gevent", "--statsd-host", "datadog:8125", "app:create_app()"]
