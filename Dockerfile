FROM python:3.7-alpine3.7

COPY ./app /app

WORKDIR /app

ENV TZ America/Chicago

RUN apk add --no-cache postgresql-libs nano bash && \
    apk add --no-cache --virtual .build-deps make gcc python-dev libffi-dev musl-dev postgresql-dev&& \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

WORKDIR /app
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
