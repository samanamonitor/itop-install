#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cp -R $DIR /opt/samana-itop/extensions
chown -R www-data.www-data /opt/samana-itop/extensions/samana-service-now
if [ -f /opt/samana-itop/conf/config-itop.php ]; then
    chmod u+w /opt/samana-itop/conf/config-itop.php
fi
