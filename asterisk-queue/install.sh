#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

echo Enter AWS SES User name
read USERNAME
echo Enter AWS SES Password
read PASSWORD
echo Enter AWS SES Server name
read SES_SERVER
echo Enter AWS SES Server port
read SES_PORT
echo Enter email recipient for report
read EMAIL_RECIPIENT

${DIR}/configure-postfix.sh $SES_SERVER $SES_PORT $USERNAME $PASSWORD

install -o root -g root -m 0755 80-sendqueuereport.cron /etc/cron.weekly
install -o root -g root -m 0755 sendqueuereport.py /usr/local/bin
install -o root -g root -m 0644 sendqueuereport /etc/default

sed -i -e "s/^EMAIL_RECIPIENT.*/EMAIL_RECIPIENT=${EMAIL_RECIPIENT}" /etc/default/sendqueuereport