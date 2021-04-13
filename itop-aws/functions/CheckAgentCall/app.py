import boto3
import sys
import os
import json

config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')
config = {}
client = boto3.client('lambda')

def handler(event, context):
    global config
    count = 0
    try:
        print("DEBUG: %s" % (json.dumps(event)))
        config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

        out = db.Table(config['outboundQueueTable']).scan()
        count = out['Count']
        for i in out['Items']:
            print('Outbound call: {}'.format(json.dumps(i)))
            p = bytearray()
            p.extend(json.dumps({
                'nexmoKey': config['nexmoKey'],
                'nexmoAppID': config['nexmoAppID'],
                'method': 'get_call',
                'uuid': i['uuid']
                }).encode())
            # TODO: replace function name with environment variable
            response = client.invoke(
                FunctionName='arn:aws:lambda:us-east-1:438136544486:function:iTopNexmoCallAgent-ITopLambdaNexmoFunction-L7Z9NODDJRI3',
                InvocationType='RequestResponse',
                Payload=p
                )
            payload = json.load(response['Payload'])
            print('Payload received: {}'.format(json.dumps(payload)))
            if payload['status'] != 'ringing' or payload['status'] != 'answered':
                response = db.Table(config['outboundQueueTable']).delete_item(Key={'uuid': i['uuid']})
                count -= 1

    except Exception as e:
        print("ERROR(%s:%d): %s %s" % (sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, type(e).__name__, e.args[0]))

    return count
