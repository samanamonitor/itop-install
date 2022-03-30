#!/bin/bash


DBPASS=$1

if [ -z "$DBPASS" ]; then
    echo "USAGE: $0 <db pass>" >&2
    exit 1
fi

SAMANA_PATH=/opt/samana-itop
DB_PATH=$SAMANA_PATH/db
DBLOG_PATH=$SAMANA_PATH/dblog

create_if_not_exist() {
    local path=$1
    if [ ! -d "$path" ]; then
        mkdir -p $path
    fi
}

IMAGE=$(docker image ls -q itop-web-img:v1)
if [ -z "$IMAGE" ]; then
    docker build -t itop-db-img:v1  . --build-arg DBPASS='$DBPASS'
fi

create_if_not_exist $DB_PATH
create_if_not_exist $DBLOG_PATH

docker run -p 3306:3306 -d \
    --mount type=bind,source="$DB_PATH",target=/var/lib/mysql \
    --mount type=bind,source="$DBLOG_PATH",target=/var/log/mysql \
    --name itop-db itop-db-img:v1 mysqld_safe