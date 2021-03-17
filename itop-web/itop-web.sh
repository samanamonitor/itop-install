#!/bin/bash
set -xe
apt update
DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata apache2 unzip \
        software-properties-common wget php7.2 php7.2-mysql php7.2-ldap php7.2-cli php7.2-soap \
        php7.2-json graphviz php7.2-xml php7.2-gd php7.2-zip libapache2-mod-php php7.2-mbstring
ln -fs /usr/share/zoneinfo/US/Eastern /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata
sed -i -e 's/memory_limit = 128M/memory_limit = 256M/g' \
        -e 's/post_max_size = 8M/post_max_size = 32M/g' \
        -e 's/; max_input_vars = 1000/max_input_vars = 4440/g' \
        -e 's/;date.timezone =/date.timezone = US\/Eastern/g'  \
       /etc/php/7.2/apache2/php.ini
/etc/init.d/apache2 start
wget -O /tmp/iTop-2.7.3-6624.zip https://sourceforge.net/projects/itop/files/itop/2.7.3/iTop-2.7.3-6624.zip
unzip /tmp/iTop-2.7.3-6624.zip -d /tmp/itop
mkdir -p /var/www/html/itop
mv /tmp/itop/web/* /var/www/html/itop
mkdir -p /var/www/html/itop/env-production /var/www/html/itop/env-production-build /var/www/html/itop/conf/production 
chown -R www-data.www-data /var/www/html/itop
rm -Rf /tmp/itop/
