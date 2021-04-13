FROM python:3

WORKDIR /usr/src/itop-asterisk
RUN pip install --no-cache-dir requests
COPY *.py ./

ENTRYPOINT [ "python", "./setqueuemembers.py" ]