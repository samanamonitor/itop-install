#!/bin/bash

if [ "$1" == "" ]; then
    echo "Required queue number"
    exit 1
fi

if ! which docker > /dev/null; then
    apt install -y docker.io
fi

if ! docker inspect itopasterisk:latest > /dev/null; then
    docker build -t itopasterisk .
fi

cat <<EOF > /etc/cron.d/itopast
MAILTO='$2'

1  *    * * *   root    docker run --name ia --rm itopasterisk $1
EOF