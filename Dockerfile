FROM python:3.7-alpine3.7

COPY ./CredentialManager /CredentialManager

WORKDIR /CredentialManager

ENV TZ America/Chicago

RUN apk add --no-cache postgresql-libs nano bash && \
    apk add --no-cache --virtual .build-deps make gcc python-dev libffi-dev musl-dev postgresql-dev&& \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

WORKDIR /CredentialManager
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "CredentialManager:app"]
