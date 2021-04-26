#!/usr/bin/python

import csv
import time
import cStringIO
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import sys

class Call:
    url = None
    callerid = None
    position = None
    origposition = '0'
    waittime = '0'
    agent = None
    holdtime = '0'
    bridgedchanneluniqueid = None
    ringtime = '0'
    calltime = '0'
    end_time = None
    def __init__(self, call_id, csv_data):
        self.id = call_id
        self.start_epoch = csv_data[0]
        self.queue_name = csv_data[2]
        self.queue_member_channel = csv_data[3]
        self.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self.start_epoch)))
        self.process_event(csv_data)
    def process_event(self, csv_data):
        if len(csv_data) < 5:
            raise AttributeError("Invalid number of parameters %s", csv_data)
        self.status  = csv_data[4].lower()
        self._event_data   = csv_data[:5]
        self._event_params = csv_data[5:]
        try:
            getattr(self, self.status)()
        except AttributeError,e:
            self.undefined()
        except Exception,e:
            raise e
    def enterqueue(self):
        if len(self._event_params) != 2:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.url                    = self._event_params[0]
        self.callerid               = self._event_params[1]
    def abandon(self):
        if len(self._event_params) != 3:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.position               = self._event_params[0]
        self.origposition           = self._event_params[1]
        self.waittime               = self._event_params[2]
        self.end_time               = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self._event_data[0])))
    def connect(self):
        if len(self._event_params) != 3:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.agent                  = self._event_data[3]
        self.holdtime               = self._event_params[0]
        self.bridgedchanneluniqueid = self._event_params[1]
        self.ringtime               = self._event_params[2]
    def exitwithtimeout(self):
        if len(self._event_params) != 3:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.position               = self._event_params[0]
        self.origposition           = self._event_params[1]
        self.waittime               = self._event_params[2]
        self.end_time               = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self._event_data[0])))
    def exitempty(self):
        if len(self._event_params) != 3:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.position               = self._event_params[0]
        self.origposition           = self._event_params[1]
        self.waittime               = self._event_params[2]
        self.end_time               = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self._event_data[0])))
    def completecaller(self):
        if len(self._event_params) != 3:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.holdtime               = self._event_params[0]
        self.calltime               = self._event_params[1]
        self.origposition           = self._event_params[2]
        self.end_time               = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self._event_data[0])))
    def completeagent(self):
        if len(self._event_params) != 3:
            raise AttributeError("Invalid number of parameters %s", self._event_params)
        self.holdtime               = self._event_params[0]
        self.calltime               = self._event_params[1]
        self.origposition           = self._event_params[2]
        self.end_time               = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self._event_data[0])))
    def undefined(self):
        pass
    def header(self):
        return [
            'id',
            'start_time',
            'end_time',
            'callerid',
            'agent',
            'holdtime',
            'waittime',
            'calltime',
            'status'
            ]
    def row(self):
        return [
            self.id,
            self.start_time,
            self.end_time,
            self.callerid,
            self.agent,
            self.holdtime,
            self.waittime,
            self.calltime,
            self.status
            ]
    def __str__(self):
        if self.callerid is None:
            return ""
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            self.id,
            self.start_time,
            self.end_time,
            self.callerid,
            self.agent,
            self.holdtime,
            self.waittime,
            self.calltime,
            self.status
            )

def log_to_csv(filename, outfile):
    calls = {}
    f = open(filename, "r")
    queue = csv.reader(f, delimiter='|', quotechar='"')
    for row in queue:
        if row[1] != 'NONE':
            if row[1] not in calls:
                calls[row[1]] = Call(row[1], row)
            else:
                calls[row[1]].process_event(row)
    f.close()
    keys = calls.keys()
    keys.sort()
    writer = csv.writer(outfile)
    writer.writerow(calls[keys[0]].header())
    for k in keys:
        if calls[k].callerid is not None:
            writer.writerow(calls[k].row())
    outfile.reset()

def sendmail(emailfrom, emailto, subject, attachment=''):
    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = subject
    msg.preamble = "PBX Queue Report"
    ctype = "text/csv"
    maintype, subtype = ctype.split("/", 1)
    attachment = MIMEText(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename='report.csv')
    msg.attach(attachment)
    server = smtplib.SMTP('localhost')
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

def main(exec_name, argv):
    if len(argv) != 2:
        print("Usage: %s <recipient email> <queue file path>")
        exit(1)

    emailfrom = "Samana PBX <pbx@samanagroup.com>"
    emailto = argv[0]
    queue_file = argv[1]
    call_csvio = cStringIO.StringIO()
    log_to_csv(queue_file, call_csvio)
    sendmail(emailfrom, emailto, "PBX Queue Report", attachment=call_csvio.read())

if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])

