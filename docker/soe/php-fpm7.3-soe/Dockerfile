# pinched from https://github.com/TrafeX/docker-php-nginx/blob/master/Dockerfile
# converted to use debian instead, then sprinkled with 'our stuff'
FROM debian:bullseye-slim

# REMEMBER TO ALSO CHANGE THE PHP VERSION IN SUPERVISORD'S CONF FILE
ENV PHP_VERSION=7.3
ENV USER=www-data
ENV DEBIAN_FRONTEND=noninteractive
ENV COMPOSER_COMMIT_HASH=836aa0551f8fb6739f54316b0dba10328932e6a4
# COMPOSER_CACHE_DIR is used by 'composer install' in the application Dockerfiles
ENV COMPOSER_CACHE_DIR=/tmp/composer

## for versions of PHP not available in the standard debian repos,
## set up sury.org before apt-get update https://packages.sury.org/php/
## (insert these lines before the 'apt-get install php' lines below)
#    && curl -s -o /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg \
#    && echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list \
#    && apt-get update \


# curl and lsb-release are really only needed if you're adding the sury repos described above
# git and unzip are needed for some 'composer install' requirements
RUN apt-get update \
    && apt-get --no-install-recommends --no-install-suggests --yes --quiet install \
        ca-certificates \
        curl \
        lsb-release \
        nginx \
        supervisor \
        git \
        unzip \
    && curl -s -o /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg \
    && echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list \
    && apt-get update \
    && apt-get --no-install-recommends --no-install-suggests --yes --quiet install \
        php${PHP_VERSION}-fpm \
        php${PHP_VERSION}-curl \
        php${PHP_VERSION}-gd \
        php${PHP_VERSION}-mbstring \
        php${PHP_VERSION}-mysql \
        php${PHP_VERSION}-redis \
        php${PHP_VERSION}-soap \
        php${PHP_VERSION}-xml \
        php${PHP_VERSION}-zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc/* /usr/share/man/* /usr/share/info/* \
    && mkdir /run/php

# Installing Composer is stupid. It's not bundled by anything, it says "run
# this script" to install, and the hash changes frequently...
# so... this is the 'programmatic install' and it's locked to a specific version
# of Composer. If we want to update the version of Composer, we specify the
# git hash listed in https://github.com/composer/getcomposer.org/commits/master
# (see https://getcomposer.org/doc/faqs/how-to-install-composer-programmatically.md)

RUN curl -s https://raw.githubusercontent.com/composer/getcomposer.org/${COMPOSER_COMMIT_HASH}/web/installer | php -- --quiet \
    && mv composer.phar /usr/local/bin/composer


# Configure nginx
# we don't run with a 'default_server' directive, and make sure our placeholder
# config is loaded last ('zz-') - this way the 'default server' will implicitly
# be the nginx vhost installed in a subsequent Dockerfile - if there is no
# 'default_server' directive, nginx takes the first vhost with a matching
# 'listen' directive
COPY config/nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/00-default
COPY config/nginx-default-vhost.conf /etc/nginx/sites-enabled/zz-default

# Configure PHP-FPM
COPY config/fpm-pool.conf /etc/php/${PHP_VERSION}/fpm/pool.d/www.conf
COPY config/php.ini /etc/php/${PHP_VERSION}/fpm/php.ini

# Configure supervisord
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

## Make sure files/folders needed by the processes are accessable when they run under the $USER
# (logging should go to stderr, but we have some cases where we have on-disk logging)
RUN chown -R $USER /run \
    && chown -R $USER /var/lib/nginx \
    && chown -R $USER /var/log/nginx

# Setup default application document root
RUN mkdir -p /var/www/html

# prep an 'app' directory for use by client Dockerfiles
RUN mkdir -p /var/www/app/vendor \
    && chown -R $USER /var/www/app

# Switch to use a non-root user from here on
USER $USER

# Add default application
WORKDIR /var/www/html
COPY config/web/ /var/www/html/

# Expose the port nginx is reachable on
EXPOSE 8080

# Let supervisord start nginx & php-fpm
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Configure a healthcheck to validate that everything is up&running
HEALTHCHECK --timeout=10s CMD curl --silent --fail http://127.0.0.1:8080/fpm-ping
