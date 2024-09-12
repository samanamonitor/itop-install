FROM python:3

WORKDIR /usr/src/itop-asterisk
RUN pip install --no-cache-dir requests

ENTRYPOINT [ "/usr/bin/timeout", "-s", "9", "1m", "python", "./setqueuemembers.py" ]