#!/bin/bash
set -xe
apt update
DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata mariadb-server
ln -fs /usr/share/zoneinfo/US/Eastern /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata
cat <<EOF > /etc/mysql/mariadb.conf.d/itop.cnf
[mysqld]
max_allowed_packet = 50M
innodb_buffer_pool_size = 512M
query_cache_size = 32M
query_cache_limit = 1M
bind-address = 0.0.0.0
EOF
/etc/init.d/mysql start
cat <<EOF | mysql
CREATE DATABASE itop;
CREATE USER itop IDENTIFIED BY '$DBPASS';
GRANT ALL PRIVILEGES ON itop.* TO 'itop'@'%';
FLUSH PRIVILEGES;
EOF
