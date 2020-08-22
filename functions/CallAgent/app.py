import sys
import os
sys.path.insert(0, "./lib")
import nexmo
import re
import json
import boto3

config = {}
config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')

def valid_phone(p):
    phone = re.sub('[^0-9+]', '', p)
    if re.match('^\+[0-9]+$', phone) is None: 
        return None
    return phone

def db_addcall_queue(uuid, data, t, p):
    try:
        result = db.Table(config['outboundQueueTable']).put_item(Item={
            "uuid": uuid,
            "phone": p,
            "time": t,
            "data": data
        })
        print("result=%s" % json.dumps(result))
    except:
        print("Unable to register call into Queue")


def handler(event, context):
    global config
    try:
        print(sys._getframe().f_code.co_name + " " + json.dumps(event))

        config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']


        if 'phone' not in event:
            raise Exception("Phone missing")

        if 'caller_id' not in event:
            raise Exception("CallerID missing")

        phone = valid_phone(event['phone'])
        if phone is None:
            raise Exception("Invalid Phone number")

        if 'time' not in event:
            t = '2000-01-01 00:00:00.000000'
        else:
            t = event['time']

        caller_id = valid_phone(event['caller_id'])
        if caller_id is None:
            raise Exception("Invalid CallerID")

        print("starting communication with nexmo")

        aurl           = config['outboundAnswerURL']
        eurl           = config['outboundEventURL']
        private_key    = '\n'.join(config['nexmoKey'].split('\\n'))

        client = nexmo.Client(application_id=config['nexmoAppID'], private_key=private_key)
        agent_call_data = client.create_call({ 
            "to": [{
                'type':'phone', 
                'number': phone
                }], 
            'from': { 
                'type': 'phone', 
                'number': caller_id
                }, 
            'answer_url': [ aurl ], 
            'event_url' : [ eurl ],
            'ringing_timer': int(config['ringTimer']),
            'machine_detection': 'hangup'
        })
        print("calling: " + json.dumps(agent_call_data))
        db_addcall_queue(agent_call_data['uuid'], agent_call_data, t, phone)
    except Exception as e:
        print("Exception: " + json.dumps(e.args))
        agent_call_data = { 'error': e.args[0] }

    print("Finished.")
    return agent_call_data
