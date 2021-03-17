run the followig command to create the image for itop-web: 
docker build -t itop-web-img:v1 .
run the following command to create the volumes:
./add-volumes.sh
run the following commands to create the container: 
docker run -p 80:80 -p 443:443 -d  \
    --mount source=conf_itop,target=/var/www/html/itop/conf/production \
    --mount source=log_itop,target=/var/log/apache2 \
    --mount source=build_itop,target=/var/www/html/itop/env-production-build \
    --mount source=prod_itop,target=/var/www/html/itop/env-production \
    --name itop-web itop-web-img:v1 /usr/sbin/apache2ctl -DFOREGROUND

