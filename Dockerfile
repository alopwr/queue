FROM library/python:alpine
RUN apk update && apk upgrade && apk add --no-cache make g++ bash git openssh postgresql-dev gcc musl-dev libffi-dev openssl-dev python3-dev cargo jpeg-dev zlib-dev
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY caprover_run.sh /usr/src/utils/
EXPOSE 80
CMD sh /usr/src/utils/caprover_run.sh
