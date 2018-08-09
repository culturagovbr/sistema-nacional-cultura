FROM python:3.6-alpine

LABEL maintainer LabLivre/UFABC team

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT True
ENV DEBUG False

RUN apk add --no-cache libpq
RUN apk add --no-cache --virtual=build-dependencies wget ca-certificates postgresql-dev gcc musl-dev linux-headers git
RUN apk add wkhtmltopdf --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted
RUN pip install pipenv
RUN adduser -D -s /bin/false -u 1000 nonroot


COPY . /code/
WORKDIR /code/
RUN chown -R nonroot: .

RUN pipenv install --deploy --ignore-pipfile 
RUN apk del build-dependencies

USER nonroot
RUN pipenv run ./manage.py collectstatic --noinput

EXPOSE 8000 8001

ENTRYPOINT ["pipenv", "run", "uwsgi", "--http", ":8000", "--wsgi-file", "snc/wsgi.py", "--master", "--stats", ":8001", "--chdir", "/code"]
