run the followig command to create the image for itop-db (Replace YOURPASSWORD with a secure password): 
docker build -t itop-db-img:v1  . --build-arg DBPASS='YOURPASSWORD'
run the following command to create the volumes:
./add-volumes.sh
run the following commands to create the container: 
docker run -p 3306:3306 -d \
    --mount source=db_itop,target=/var/lib/mysql \
    --mount source=dblog_itop,target=/var/log/mysql \
    --name itop-db itop-db-img:v1 mysqld_safe

