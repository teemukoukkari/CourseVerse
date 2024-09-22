FROM python:3.11-alpine

WORKDIR /usr/src

COPY requirements.txt requirements.txt
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]