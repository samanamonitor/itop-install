#!/bin/bash

SAMANA_PATH=/opt/samana-itop
dirs="conf log prod build extensions"

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

IMAGE=$(docker image ls -q itop-web-img:v1)
if [ -z "$IMAGE" ]; then
    docker build -t itop-web-img:v1 .
fi
for d in $dirs; do
    create_bind $d
done

chmod +rx /var/lib/docker/volumes
chmod +r /var/lib/docker/


docker run -p 80:80 -p 443:443 -d  \
    --mount source=itop_conf,target=/var/www/html/itop/conf/production \
    --mount source=itop_log,target=/var/log/apache2 \
    --mount source=itop_build,target=/var/www/html/itop/env-production-build \
    --mount source=itop_prod,target=/var/www/html/itop/env-production \
    --mount source=itop_extensions,target=/var/www/html/itop/extensions \
    --name itop-web itop-web-img:v1 /usr/sbin/apache2ctl -DFOREGROUND
