#!/bin/bash
mkdir -p /opt/samana-itop/
docker volume create db_itop
docker volume create dblog_itop
ln -s $(docker inspect db_itop | jq -r .[0].Mountpoint) /opt/samana-itop/db
ln -s $(docker inspect dblog_itop | jq -r .[0].Mountpoint) /opt/samana-itop/dblog
chmod +rx /var/lib/docker/volumes
chmod +r /var/lib/docker/
echo "Volumes created"
