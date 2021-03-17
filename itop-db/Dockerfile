FROM ubuntu:bionic as itop-db-img
EXPOSE 3306
COPY itop-db.sh /tmp/itop-db.sh
WORKDIR /tmp
ARG DBPASS
RUN /tmp/itop-db.sh
