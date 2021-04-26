* Instructions to install Samana PBX

1. Copy sendqueuereport.py to /usr/local/bin
2. chmod +x /usr/local/bin/sendqueuereport.py
3. Copy 80-sendqueuereport.cron to /etc/cron.weekly
4. chmod +x /etc/cron.weekly/80-sendqueuereport.cron
5. Copy sendqueuereport to /etc/default
6. Set appropiate recipient email in /etc/default/sendqueuereport