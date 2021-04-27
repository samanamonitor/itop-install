
publish: asterisk-queue.tgz
	aws s3 cp $< s3://phoneweb --acl public-read

asterisk-queue.tgz:
	mkdir asterisk-queue
	cp 80-sendqueuereport.cron asterisk-queue
	cp configure-postfix.sh asterisk-queue
	cp sendqueuereport asterisk-queue
	cp sendqueuereport.py asterisk-queue
	cp install.sh asterisk-queue
	tar -czvf $@ asterisk-queue/*
	rm -Rf asterisk-queue

clean:
	rm asterisk-queue.tgz