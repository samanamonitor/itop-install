FROM python:3

WORKDIR /usr/src/itop-asterisk
RUN pip install --no-cache-dir requests
COPY *.py ./

CMD [ "python", "./setqueuemembers.py", "6002" ]