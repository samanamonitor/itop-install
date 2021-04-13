import json
from requests import post



class iTopManager:
    def __init__(self, username, secret, host='localhost', port='80', 
            protocol='http', path='/itop/webservices/rest.php', itop_rest_version='1.3'):
        self.username = username
        self.secret = secret
        self.host = host
        self.port = port
        self.protocol = protocol
        self.path = path
        self.itop_rest_version = itop_rest_version

    def query(self, operation, classname, key, output_fields):
        json_data = {
            "operation":operation,
            "class":classname,
            "key":key,
            "output_fields":output_fields
        }
        self.data = {
            'version': self.itop_rest_version,
            'json_data': json.dumps(json_data),
            'auth_user': self.username,
            'auth_pwd': self.secret
        }
        res = post("%s://%s:%s%s" % (self.protocol, self.host, self.port, self.path), data=data)
        return res.json()

    def get_scheduled_members(self):
        members = self.query(operation="core/get", classname="OnCall", key="SELECT OnCall "
            "WHERE DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00') >= day "
            "AND   DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00') <= repeat_until_end_of "
            "AND   DATE_FORMAT(NOW(),'%T') >= DATE_FORMAT(start_time,'%T')"
            "AND   DATE_FORMAT(NOW(),'%T') < DATE_FORMAT(end_time,'%T')"
            "AND  (type = 'Primary' OR type = 'Backup' OR type = 'Manager')",
            output_fields="number,email,type")
        qmembers_sched = []
        for o in jsonRes['objects'].keys():
            qmembers_sched += [jsonRes['objects'][o]['fields']['number']]
        return qmembers_sched
