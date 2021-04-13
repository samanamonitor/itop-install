import boto3
import sys
import os
import json

config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')
config = {}

def handler(event, context):
    global config
    caller = ''
    try:
        print("DEBUG: %s" % (json.dumps(event)))

        config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

        out = db.Table(config['InboundQueueTable']).scan()
        if out['Count'] == 0: return 0

        uuid = out['Items'][0]['uuid']
        caller = db.Table(config['InboundCallTable']).get_item(
                Key={ 'uuid': uuid})['Item']['status']
    except Exception as e:
        print("ERROR(%s:%d): %s %s" % (sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, type(e).__name__, e.args[0]))

    if caller == 'waiting':
        print("DEBUG: Caller is waiting")
        return 1
    else:
        print("DEBUG: Caller is NOT waiting")
        return 0
