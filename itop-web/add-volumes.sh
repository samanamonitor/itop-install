#!/bin/bash
mkdir -p /opt/samana-itop/
docker volume create conf_itop
docker volume create log_itop
docker volume create prod_itop
docker volume create build_itop
ln -s $(docker inspect conf_itop | jq -r .[0].Mountpoint) /opt/samana-itop/conf
ln -s $(docker inspect log_itop | jq -r .[0].Mountpoint) /opt/samana-itop/log
ln -s $(docker inspect prod_itop | jq -r .[0].Mountpoint) /opt/samana-itop/prod
ln -s $(docker inspect build_itop | jq -r .[0].Mountpoint) /opt/samana-itop/build
chmod +rx /var/lib/docker/volumes
chmod +r /var/lib/docker/
echo "Volumes created"
