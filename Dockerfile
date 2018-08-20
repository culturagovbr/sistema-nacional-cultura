FROM python:3.6-alpine

LABEL maintainer LabLivre/UFABC team

ARG RAVEN_DSN_URL
ARG DEBUG

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT True
ENV DEBUG $DEBUG
ENV RAVEN_DSN_URL $RAVEN_DSN_URL

RUN apk add --no-cache libpq libffi-dev zlib-dev jpeg-dev
RUN apk add --no-cache --virtual=build-dependencies wget ca-certificates postgresql-dev gcc musl-dev linux-headers git
RUN pip install pipenv
RUN adduser -D -s /bin/false -u 1000 nonroot


COPY . /code/
WORKDIR /code/

RUN apk -U --no-cache upgrade && \
	apk add cairo pango --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted && \
	apk add --no-cache libpq ca-certificates && \
	apk add --no-cache --virtual=build-dependencies wget postgresql-dev gcc musl-dev linux-headers git libffi-dev zlib-dev jpeg-dev cairo-dev pango-dev && \
	pip install pipenv && \
	adduser -D -s /bin/false -u 1000 nonroot && \
	pipenv install --system --deploy --ignore-pipfile && \
	apk del build-dependencies && \
	python ./manage.py collectstatic --noinput

EXPOSE 8000 8001

USER nonroot
ENTRYPOINT ["uwsgi", "--http", ":8000", "--wsgi-file", "snc/wsgi.py", "--master", "--stats", ":8001", "--chdir", "/code"]
