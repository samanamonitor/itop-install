import sys
import os
sys.path.insert(0, "./lib")
import json
import boto3
from datetime import tzinfo, timedelta, datetime
import urllib.parse
from requests import post
from requests.auth import HTTPBasicAuth

config_table = os.environ['config_table']
db           = boto3.resource('dynamodb', region_name='us-east-1')

"""
Code extracted from Python documentation 
https://docs.python.org/2/library/datetime.html

Start
"""
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt

DSTSTART_2007 = datetime(1, 3, 8, 2)
DSTEND_2007 = datetime(1, 11, 1, 1)
DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
DSTEND_1987_2006 = datetime(1, 10, 25, 1)
DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006

class USTimeZone(tzinfo):
    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname
    def __repr__(self):
        return self.reprname
    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname
    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)
    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self
        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO
        start = first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = first_sunday_on_or_after(dstend.replace(year=dt.year))
        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT")

"""
Code extracted from Python documentation 
https://docs.python.org/2/library/datetime.html

End
"""
def extract_contact(u):
    out = []
    for v in u['values']:
        user = {
            'id': '',
            'name': '',
            'phones': [],
            'mail': []
        }
        if 'value' in v:
            if 'user_id' in v['value']:
                user['id'] = v['value']['user_id']
            if 'phone' in v['value']:
                user['phones'] += v['value']['phone']
            if 'mail' in v['value']:
                user['mail'] += v['value']['mail']
            if 'name' in v['value']:
                user['name'] = v['value']['name']
            out.append(user)
    return out

def notnone(val1, val2, default):
    if val1 is not None:
        return val1
    elif val2 is not None:
        return val2
    else:
        return default

def debug(funcname, lineno, msg):
    if 'logLevel' not in config:
        return
    if config['logLevel'] >= 3:
        print("DEBUG(%s:%d): %s" % (funcname, lineno, msg))

def fetch_oncall_numbers():
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "fetching OnCall numbers")
    global config

    config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

    itop_ip     = config['itop_ip']
    itop_user   = config['itop_user']
    itop_pw     = config['itop_pw']

    itop_rest_version = "1.3"
    json_data = {
        "operation":"core/get",
        "class":"OnCall","key":"SELECT OnCall "\
            "WHERE day = DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00')",
        "output_fields":"primary,backup,manager"
    }

    query_str = urllib.parse.urlencode({
        'version': itop_rest_version, 
        'json_data': json.dumps(json_data)
    })
    
    res = post(
        'http://' + itop_ip + '/itop/webservices/rest.php?' + query_str,
        auth=HTTPBasicAuth(itop_user, itop_pw)
    )
    jsonRes = res.json()
    return jsonRes.get('objects').popitem()[1].get('fields')

def error(funcname, lineno, msg):
    print("ERROR(%s:%d): %s" % (funcname, lineno, msg))

def lambda_handler(event, context):

    config =  db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

    contacts = {
        'primary': [config['defaultContact']],
        'backup': [config['defaultContact']],
        'manager': [config['defaultContact']]
    }

    try:
        numbers = fetch_oncall_numbers()
        if numbers.get('primary'):
            contacts['primary'] = numbers.get('primary')
        if numbers.get('backup'):
            contacts['backup'] = numbers.get('backup')
        if numbers.get('manager'):
            contacts['manager'] = numbers.get('manager')
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "ERROR(lambda_handler): %s %s" % (type(e).__name__, e.args[0]))


    return contacts
