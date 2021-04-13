#!/bin/bash

if [ "$1" == "" ]; then
    echo "Required queue number"
    exit 1
fi

if ! which docker > /dev/null; then
    apt install -y docker.io
fi

docker build -t itopasterisk .
cat <<EOF >> /etc/crontab
1 *    * * *   root    docker run --name ia -it --rm itopasterisk $1
EOF