#!/bin/bash
#
# ami: ami-064519b8c76274859
# size: t2-small
# keypair: fabianb
# vpc: vpc-0c583fa71b94beb5e
# subnet: subnet-01ce7d0ecdae59b86
# autoassign public: true
# security-group: sg-0455730d728e30c1e
# storage: 20G
# role: arn:aws:iam::438136544486:instance-profile/SamanaPBX

dd if=/dev/zero of=/swap bs=1M count=4k
chmod 600 /swap
mkswap /swap
echo "/swap    none    swap    sw,comment=samana   0    0" >> /etc/fstab
swapon -a

apt update && apt upgrade -y
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
apt install -y wget python3-boto3
wget https://github.com/FreePBX/sng_freepbx_debian_install/raw/master/sng_freepbx_debian_install.sh -O /tmp/sng_freepbx_debian_install.sh
bash /tmp/sng_freepbx_debian_install.sh

sed -i -e "s/^relayhost.*/relayhost = [email-smtp.eu-west-2.amazonaws.com]:587/" /etc/postfix/main.cf


aws s3api get-object --bucket samanaphone --key sendqueuereport/sendqueuereport.cron /etc/cron.d/sendqueuereport
aws s3api get-object --bucket samanaphone --key sendqueuereport/sendqueuereport.default /etc/default/sendqueuereport
aws s3api get-object --bucket samanaphone --key sendqueuereport/sendqueuereport.py /usr/local/bin/sendqueuereport.py
chmod +x /usr/local/bin/sendqueuereport.py
aws s3api get-object --bucket samanaphone --key sendqueuereport/sendqueuereport.sh /usr/local/bin/sendqueuereport.sh
chmod +x /usr/local/bin/sendqueuereport.sh
mkdir -p /var/spool/asterisk/backup/
aws s3api get-object --bucket samanaphone --key pbxbackup /var/spool/asterisk/backup/pbxbackup.tar.gz

fwconsole backup --restore=/var/spool/asterisk/backup/pbxbackup.tar.gz

cat <<EOF > /etc/apache2/sites-available/redirect.conf
<VirtualHost *:80>
RewriteEngine  on
RewriteRule    "^/$"  "/admin"  [R]
</VirtualHost>
EOF
a2ensite redirect
systemctl reload apache2



#fwconsole backup --backup 575a5bdc-1ae2-4b36-bd1a-5043d540a217
#aws s3api put-object --bucket samanaphone --key pbxbackup --body /var/spool/asterisk/backup/20240911-191458-1726082098-17.0.19.9-1648199187.tar.gz




