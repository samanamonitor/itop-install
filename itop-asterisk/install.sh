#!/bin/bash

set -xe

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

usage() {
    echo "$0 <config name> <queue number>"
    exit 1
}

install_redhat() {
    sudo yum remove docker \
        docker-client \
        docker-client-latest \
        docker-common \
        docker-latest \
        docker-latest-logrotate \
        docker-logrotate \
        docker-engine
    sudo yum install -y yum-utils
    sudo yum-config-manager \
        --add-repo \
        https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum udate
    sudo yum install docker-ce docker-ce-cli containerd.io jq
}

install_debian() {
    sudo apt-get remove docker docker-engine docker.io containerd runc
    sudo apt-get update
    sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) \
signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io jq
}

if [ "$(id -u)" != "0" ]; then
    echo "Need to be root to install"
    usage
fi

if [ $# != 2 ]; then
    usage
fi

config_name=$1
queue_number=$2

INSTALL_DIR=/opt/$config_name

if [ -d $INSTALL_DIR ]; then
    echo "Install $config_name already exists. Remove old config from /opt/$config_name ."
    usage
fi

if [ -f /etc/cron.d/itopast_${config_name} ]; then
    echo "Cron task still exists. Remove it before continuing. (/etc/cron.d/itopast_${config_name})"
    usage
fi

if ! which docker > /dev/null || [ "$(docker --version | cut -d"," -f 1 | cut -d" " -f3 | cut -d"." -f1)" -lt "18" ]; then
    if [ -f /etc/redhat-release ]; then
        install_redhat
    elif [ -f /etc/debian_version ]; then
        install_ubuntu
    else
        echo "This install will only work in Debian, Ubuntu or Centos."
        usage $0
    fi
fi

echo "Asterisk-iTop integration installation script"
echo "Please provide the following information for Asterisk Server:"
if [ -z $ast_hostname ]; then
    read -p "IP/Hostname: " ast_hostname
fi
if [ -z $ast_port ]; then
    read -p "Web Manager Port: " ast_port
fi
if [ -z $ast_prefix ]; then
    read -p "Web Manager prefix: " ast_prefix
fi
if [ -z $ast_username ]; then
    read -p "Manager username: " ast_username
fi
if [ -z $ast_secret ]; then
    read -srp "Manager password: " ast_secret
    echo
fi
echo "Please provide the following information for iTop Server:"

if [ -z $itop_host ]; then
    read -p "iTop IP/Hostname: " itop_host
fi
if [ -z $itop_port ]; then
    read -p "iTop Port: " itop_port
fi
if [ -z $itop_user ]; then
    read -p "iTop Username: " itop_user
fi
if [ -z $itop_pw ]; then
    read -srp "iTop Password: " itop_pw
    echo
fi

mkdir -p ${INSTALL_DIR}
install -o root -g root ${DIR}/astmanager.py ${INSTALL_DIR}
install -o root -g root ${DIR}/itopmanager.py ${INSTALL_DIR}
install -o root -g root ${DIR}/setqueuemembers.py ${INSTALL_DIR}
cat <<EOF > ${INSTALL_DIR}/config.py
itop_pw='$itop_pw'
itop_user='$itop_user'
itop_host='$itop_host'
itop_port='$itop_port'

ast_secret='$ast_secret'
ast_username='$ast_username'
ast_host='$ast_hostname'
ast_port='$ast_port'
ast_prefix='$ast_prefix'
EOF


docker_data=$(docker image inspect itopasterisk:latest 2>/dev/null)
rc=$?

if [ "$rc" != "0" ]; then
    docker build -t itopasterisk .
else
    tags=($(echo $docker_data | jq -r .[0].RepoTags[]))
    for t in ${tags[*]}; do
        v=${t%%*:}
        if [ "$v" == "latest" ]; then
            continue
        fi
    done
    cur_version=$(cat ${DIR}/VERSION)
    if [ "$v" != "$cur_version" ]; then
        docker image rm itopasterisk:latest
        docker build -t itopasterisk:$cur_version .
        docker image tag itopasterisk:$cur_version itopasterisk:latest
    fi
fi

cat <<EOF > /etc/cron.d/itopast_${config_name}
*/5  *    * * *   root    docker run --name ia_${config_name} --rm --mount type=bind,source="${INSTALL_DIR}",target="/usr/src/itop-asterisk" itopasterisk:latest ${queue_number}
EOF
