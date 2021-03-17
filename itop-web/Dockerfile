FROM ubuntu:bionic as itop-web-img
EXPOSE 80
EXPOSE 443
COPY itop-web.sh /tmp/itop-web.sh
WORKDIR /tmp
RUN /tmp/itop-web.sh
