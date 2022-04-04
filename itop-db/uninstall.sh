#!/bin/bash

SAMANA_PATH=/opt/samana-itop
dirs="db dblog"

delete_dir_if_exist() {
    local path=$1
    if [ -d "$path" ]; then
        rmdir -p $path
    fi
}

delete_vol_if_exist() {
    local vol_name=$1
    local found
    found=$(docker volume ls -q -f name=$vol_name)
    if [ -n "$found" ]; then
        docker volume rm $vol_name
    fi
}

delete_lnk_if_exist() {
    local vol=$1
    local lnk=$2
    if [ -L $lnk ]; then
        rm $lnk
    fi
}

delete_bind() {
    local dir=$1
    delete_vol_if_exist itop_$dir
    delete_lnk_if_exist itop_$dir $SAMANA_PATH/$dir
}

docker stop itop-db
docker rm itop-db

for d in $dirs; do
    delete_bind $d
done
