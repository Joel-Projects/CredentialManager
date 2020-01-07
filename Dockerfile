FROM python:3.7-alpine3.7

<<<<<<< HEAD
COPY ./app /app

WORKDIR /app
=======
COPY ./CredentialManager /CredentialManager

WORKDIR /CredentialManager
>>>>>>> 4008f57c5fe8308021b43842101c90455de69b64

ENV TZ America/Chicago

RUN apk add --no-cache postgresql-libs nano bash && \
    apk add --no-cache --virtual .build-deps make gcc python-dev libffi-dev musl-dev postgresql-dev&& \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

<<<<<<< HEAD
WORKDIR /app
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
=======
WORKDIR /CredentialManager
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "CredentialManager:app"]
>>>>>>> 4008f57c5fe8308021b43842101c90455de69b64
