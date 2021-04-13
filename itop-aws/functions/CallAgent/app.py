import sys
import os
sys.path.insert(0, "./lib")
import vonage
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

        inbound_to = event.get('inbound_to', None)
        if inbound_to is not None:
            new_config = db.Table(config_table).get_item(Key={
                "Key": inbound_to
                })['Item']['Value']
            config.update(new_config)
            debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno,
                "Merging configurations for %s %s" % (inbound_to, config))

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
        print("before vonage")

        client = vonage.Client(application_id=config['nexmoAppID'], private_key=private_key)
        call_data = { 
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
        }
        print("before call %s" % call_data)
        agent_call_data = client.create_call(call_data)
        print("calling: " + json.dumps(agent_call_data))
        db_addcall_queue(agent_call_data['uuid'], agent_call_data, t, phone)
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno,
                "Exception: %s" % e)
        agent_call_data = {}

    print("Finished.")
    return agent_call_data

def debug(funcname, lineno, msg):
    if 'logLevel' not in config:
        return
    if config['logLevel'] >= 3:
        print("DEBUG(%s:%d): %s" % (funcname, lineno, msg))

def error(funcname, lineno, msg):
    print("ERROR(%s:%d): %s" % (funcname, lineno, msg))

