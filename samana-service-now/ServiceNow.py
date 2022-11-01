from requests import Request, Session


username='samanapiuser'
password='T$m4qAr2CZ'
url='https://siteonedev.service-now.com/api/now/table'
itopurl='http://[2607:f998:87:8:f816:3eff:fea3:c23f]'

class ServiceNow:
    def __init__(self, username, password, service_name):
        self.username=username
        self.password = password
        self.url='https://%s.service-now.com/api/now/table' % service_name
        self.s = Session()
    def sn_table(self, table, offset=0, limit=100, **kwargs):
        params={
            'sysparm_limit': limit,
            'sysparm_offset': offset}
        headers={}
        for k in kwargs.keys():
            params[k] = kwargs[k]
        result=[]
        cont=True
        while cont:
            req = Request('GET', "%s/%s" % (url, table), params=params, headers=headers, auth=(username, password))
            prepped = req.prepare()
            resp = self.s.send(prepped, timeout=5)
            temp = resp.json()['result']
            params['sysparm_offset'] += limit
            result += temp
            if len(temp) < limit:
                cont = False
        return result

class ITop:
    def __init__(self, username, password, url):
        self.username=username
        self.password=password
        self.url="%s/itop/webservices/rest.php" % url
        self.s = Session()
    def login(self):
        json_data={'operation': 'list_operations'}
        data={'version': 1.3, 'json_data': json.dumps(json_data)}
        req = Request('POST', self.url, data=data, headers={}, params={}, auth=(self.username, self.password))
        prepped = req.prepare()
        resp = self.s.send(prepped, timeout=5)
        if resp.ok is False:
            raise Exception
    def get(self, itop_class, key, output_fields):
        json_data={
            "operation":"core/get",
            "class":itop_class,
            "key":key,
            "output_fields": output_fields
            }
        data={'version': 1.3, 'json_data': json.dumps(json_data)}
        req = Request('POST', self.url, data=data, headers={}, params={})
        prepped = req.prepare()
        resp = self.s.send(prepped, timeout=5)
        if resp.ok is False:
            raise Exception
        return resp.content



        key={
                "email"="email@test.com", 
                "org_id"=3
                }
        output_fields="name,org_id,id,email"
params={
    'sysparm_limit': 100,
    'sysparm_offset': 0,
    'sysparm_display_value': True # this paramenter will pull comments and notes
}
params={
    'sysparm_limit': 100,
    'sysparm_offset': 0,
    'assignment_group': '4d2bdb1d4f6cf240abff495d0210c75e',
    'active': True,
    'sysparm_fields': "number"
}
headers={}
sysparm_fields

def user(id):
    params={
        'sysparm_limit': 100,
        'sysparm_offset': 0,
    }
    req = Request('GET', "%s/sys_user/%s" % (url, id), params=params, headers=headers, auth=(username, password))
    prepped = req.prepare()
    resp = s.send(prepped, timeout=5)
    return resp.json()

def incident(id, offset=0, **kwargs):
    params={
        'sysparm_limit': 100,
        'sysparm_offset': offset,
        'assignment_group': '4d2bdb1d4f6cf240abff495d0210c75e',
    }
    req = Request('GET', "%s/incident" % url, params=params, headers=headers, auth=(username, password))
    prepped = req.prepare()
    resp = s.send(prepped, timeout=5)
    return resp.json()

def comm(r):
    for i in r['result']:
        print(i['comments_and_work_notes'])



print(resp.status_code)

r = requests.get(url + '', 
        )

params={
    'sysparm_limit': 100,
    'sysparm_offset': 0,
    'element_id': '22311da6db1bb4508d5905d2ca9619f7'
}
req = Request('GET', "%s/sys_journal_field" % url, params=params, headers=headers, auth=(username, password))

req = Request('GET', "%s/incident/%s" % (url, '22311da6db1bb4508d5905d2ca9619f7'), params=params, headers=headers, auth=(username, password))

