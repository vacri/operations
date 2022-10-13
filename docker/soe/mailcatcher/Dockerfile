# copied from https://hub.docker.com/r/schickling/mailcatcher/dockerfile
FROM ruby:2.4-alpine3.6

LABEL maintainer="LKG IT admin"

ARG MAILCATCHER_VERSION=0.7.1

RUN set -xe \
    && apk add --no-cache \
        libstdc++ \
        sqlite-libs \
    && apk add --no-cache --virtual .build-deps \
        build-base \
        sqlite-dev \
    && gem install mailcatcher -v $MAILCATCHER_VERSION --no-ri --no-rdoc \
    && apk del .build-deps

# smtp port
EXPOSE 1025

# webserver port
EXPOSE 1080

CMD ["mailcatcher", "--no-quit", "--foreground", "--ip=0.0.0.0"]
