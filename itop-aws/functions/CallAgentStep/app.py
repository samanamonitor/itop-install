import boto3
import json
from datetime import datetime
import os
import sys

config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')

config = {}

def handler(event, context):
    global config

    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(event))
    try:

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
                "Merging configurations for %s" % inbound_to)

        out = db.Table(config['InboundQueueTable']).scan()
        if out['Count'] == 0: 
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "No calls on queue")
            return {}

        inbound_uuid = out['Items'][0]['uuid']
        inbound_phone = out['Items'][0]['from']
        inbound_conversation_uuid = out['Items'][0]['conversation_uuid']

        out = db.Table(config['outboundQueueTable']).scan()
        if out['Count'] > 0:
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "Already attempting to concact agent. Skipping")
            return {}

        call = db.Table(config['InboundCallTable']).get_item(Key={ 
            "uuid": inbound_uuid
        })
        if call['Item']['status'] != 'waiting':
            # TODO: remove item from list
            return {}

        callstart = datetime.strptime(
            call['Item']['timestamp'], 
            '%Y-%m-%dT%H:%M:%S.%fZ')
        now = datetime.utcnow()
        delta = now - callstart
        agent_data = call['Item']['agent_data']
        if delta.seconds > config['timeToFallback']:
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "Calling Fallback")
            phone = agent_data['fallback'][0]['phones'][0]
            email = agent_data['fallback'][0]['mail'][0]
        elif delta.seconds > config['timeToManager']:
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "Calling Manager")
            phone = agent_data['manager'][0]['phones'][0]
            email = agent_data['manager'][0]['mail'][0]
        elif delta.seconds > config['timeToBackup']:
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "Calling Backup")
            phone = agent_data['backup'][0]['phones'][0]
            email = agent_data['backup'][0]['mail'][0]
        else:
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "Calling Primary")
            phone = agent_data['primary'][0]['phones'][0]
            email = agent_data['primary'][0]['mail'][0]

        
        send_email(email, inbound_phone, inbound_conversation_uuid)
        out = call_agent(phone, inbound_to)
        out['phonenumber'] = phone
        db_register_outbound(out, inbound_uuid, phone)
        db_addcall_outqueue(out)
        out.update(event)
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unknown error. %s %s" % ( type(e).__name__, e.args[0]))
        out = {}

    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "Finished. out=%s" % json.dumps(out))

    return out

def call_agent(phone, inbound_to):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "phone=%s" % phone)
    try:
        client = boto3.client('lambda')
        p = bytearray()
        p.extend(json.dumps({
                'phone': phone,
                'caller_id': config['callerID'],
                'time': datetime.now().isoformat(' '),
                'inbound_to': inbound_to
                }).encode())
        # TODO: replace function name with environment variable
        response = client.invoke(
            FunctionName='iTopNexmoCallAgent-ITopCallAgentFunction-1GXGABIEYLFJY',
            InvocationType='RequestResponse',
            Payload=p
            )
        payload = response['Payload'].read()
        debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno, 
                "payload=%s" % payload)
        out = json.loads(payload)
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "%s %s" % (type(e).__name__, e.args[0]))
        out = {}
    return out

def db_register_outbound(agent_call_data, inbound_uuid, phones):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "agent_call_data=%s inbound_uuid=%s phones=%s" % 
            (json.dumps(agent_call_data), inbound_uuid, phones))
    try:
        table = db.Table(config['outboundCallTable'])
        newcall_data = table.put_item(Item={
            "uuid": agent_call_data['uuid'],
            "caller_uuid": inbound_uuid,
            "direction": agent_call_data['direction'],
            "conversation_uuid": agent_call_data['conversation_uuid'],
            "status": agent_call_data['status'],
            "phones": phones
        });
        print("newcall_data: " + json.dumps(newcall_data))
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "Unable to register outbound call. %s %s" % (type(e).__name__, e.args[0]))

def db_addcall_outqueue(data):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "data=%s" % 
            json.dumps(data))
    try:
        db.Table(config['outboundQueueTable']).put_item(Item={
            "uuid": data['uuid'],
            "data": data
        })
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "Unable to register call into Queue. %s %s" % (type(e).__name__, e.args[0]))

def send_email(email, inbound_phone, conversation_uuid):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "email=%s phone=%s" % (email, inbound_phone))

    client = boto3.client('ses')
    
    message = config['emailMessage']
    try:
        response = client.send_email(
            Source=config['sourceEmail'],
            Destination={
                'ToAddresses': [
                    email,
                ]
            },
            Message={
                'Subject': {
                    'Data': config['emailSubject'] % inbound_phone,
                    'Charset': 'utf8'
                },
                'Body': {
                    'Text': {
                        'Data': message % (inbound_phone, conversation_uuid),
                        'Charset': 'utf8'
                    }
                }
            }
        )
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "%s %s" % (type(e).__name__, e.args[0]))
        response = {}

    return response

def debug(funcname, lineno, msg):
    if 'logLevel' not in config:
        return
    if config['logLevel'] >= 3:
        print("DEBUG(%s:%d): %s" % (funcname, lineno, msg))

def info(funcname, lineno, msg):
    if 'logLevel' not in config:
        return
    if config['logLevel'] >= 2:
        print("INFO(%s:%d) %s" %  (funcname, lineno, msg))

def warn(funcname, lineno, msg):
    if 'logLevel' not in config:
        return
    if config['logLevel'] >= 1:
        print("WARN(%s:%d): %s" % (funcname, lineno, msg))

def error(funcname, lineno, msg):
    print("ERROR(%s:%d): %s" % (funcname, lineno, msg))
