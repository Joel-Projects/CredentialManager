FROM python:3.9-alpine

COPY ./app /opt/www/CredentialManager/app
COPY ./config.py /opt/www/CredentialManager/config.py
COPY ./gunicorn.conf.py /opt/www/CredentialManager/gunicorn.conf.py
COPY ./flask_restplus_patched /opt/www/CredentialManager/flask_restplus_patched

WORKDIR /opt/www/CredentialManager/app

ENV TZ America/Chicago
ENV FLASK_CONFIG production

RUN apk add --no-cache postgresql-libs nano bash && \
    apk add --no-cache --virtual .build-deps alpine-sdk build-base make gcc libffi-dev musl-dev postgresql-dev && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

WORKDIR /opt/www/CredentialManager/

EXPOSE 5000

CMD ["gunicorn"]
