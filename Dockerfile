FROM alpine:3.8

LABEL maintainer LabLivre/UFABC team

ARG RAVEN_DSN_URL
ARG DEBUG

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT True
ENV DEBUG $DEBUG
ENV RAVEN_DSN_URL $RAVEN_DSN_URL

COPY . /code/
WORKDIR /code/

RUN apk -U --no-cache upgrade && \
	apk add --no-cache python3 libpq ca-certificates cairo-gobject cairo pango libffi glib jpeg && \
	apk add --no-cache --virtual=build-dependencies python3-dev wget postgresql-dev gcc musl-dev linux-headers git libffi-dev zlib-dev jpeg-dev cairo-dev pango-dev && \
	pip3 install pipenv && \
	pipenv install --dev --system --deploy --ignore-pipfile && \
	apk del build-dependencies && \
	python3 ./manage.py collectstatic --noinput && \
	adduser -D -s /bin/false -u 1000 nonroot && \
	chown -R nonroot: *

EXPOSE 8000 8001

USER nonroot
ENTRYPOINT ["uwsgi", "--http", ":8000", "--wsgi-file", "snc/wsgi.py", "--master", "--stats", ":8001", "--chdir", "/code"]
