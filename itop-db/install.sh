#!/bin/bash


DBPASS=$1

if [ -z "$DBPASS" ]; then
    echo "USAGE: $0 <db pass>" >&2
    exit 1
fi

SAMANA_PATH=/opt/samana-itop
dirs="db dblog"

create_dir_if_not_exist() {
    local path=$1
    if [ ! -d "$path" ]; then
        mkdir -p $path
    fi
}

create_vol_if_not_exist() {
    local vol_name=$1
    local found
    found=$(docker volume ls -q -f name=$vol_name)
    if [ -z "$found" ]; then
        docker volume create $vol_name
    fi
}

create_lnk_if_not_exist() {
    local vol=$1
    local lnk=$2
    if [ ! -l $lnk ]; then
        ln -s $(docker inspect $vol | jq -r .[0].Mountpoint) $lnk
    fi
}

create_bind() {
    local dir=$1
    create_vol_if_not_exist itop_$dir
    create_lnk_if_not_exist itop_$dir $SAMANA_PATH/$dir
}

create_dir_if_not_exist $SAMANA_PATH

IMAGE=$(docker image ls -q itop-db-img:v1)
if [ -z "$IMAGE" ]; then
    docker build -t itop-db-img:v1 .
fi
for d in $dirs; do
    create_bind $d
done

chmod +rx /var/lib/docker/volumes
chmod +r /var/lib/docker/

docker run -p 3306:3306 -d \
    --mount source=itop_db,target=/var/lib/mysql \
    --mount source=itop_dblog,target=/var/log/mysql \
    --name itop-db itop-db-img:v1 mysqld_safe