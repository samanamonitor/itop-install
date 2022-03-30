#!/bin/bash

SAMANA_PATH=/opt/samana-itop
CONF_PATH=$SAMANA_PATH/conf
LOG_PATH=$SAMANA_PATH/log
BUILD_PATH=$SAMANA_PATH/build
PROD_PATH=$SAMANA_PATH/prod
EXTENSIONS_PATH=$SAMANA_PATH/extensions

create_if_not_exist() {
    local path=$1
    if [ ! -d "$path" ]; then
        mkdir -p $path
    fi
}

IMAGE=$(docker image ls -q itop-web-img:v1)
if [ -z "$IMAGE" ]; then
    docker build -t itop-web-img:v1 .
fi

create_if_not_exist $CONF_PATH
create_if_not_exist $LOG_PATH
create_if_not_exist $BUILD_PATH
create_if_not_exist $PROD_PATH
create_if_not_exist $EXTENSIONS_PATH

docker run -p 80:80 -p 443:443 -d  \
    --mount type=bind,source="$CONF_PATH",target=/var/www/html/itop/conf/production \
    --mount type=bind,source="$LOG_PATH",target=/var/log/apache2 \
    --mount type=bind,source="$BUILD_PATH",target=/var/www/html/itop/env-production-build \
    --mount type=bind,source="$PROD_PATH",target=/var/www/html/itop/env-production \
    --mount type=bind,source="$EXTENSIONS_PATH",target=/var/www/html/itop/extensions \
    --name itop-web itop-web-img:v1 /usr/sbin/apache2ctl -DFOREGROUND