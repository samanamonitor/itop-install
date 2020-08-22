import sys
import os
import boto3
import json
from datetime import datetime

config_table = os.environ['config_table']
db                  = boto3.resource('dynamodb', region_name='us-east-1')
app_url             = ''
config = {}

caller_data = {}
agent_data = {}

def handler(event, context):
    response = {}
    
    global app_url
    global config
    app_url = "https://" + event['params']['header']['Host'] + "/" + event['context']['stage']
    try:

        config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

        debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno, 
                json.dumps(event))

        qs = event['context']['resource-path'].split('/')
        action = qs[1]
        direction = qs[2]

        if action == 'event':
            if 'status' in event['body-json']:
                action = event['body-json']['status']
            elif 'type' in event['body-json']:
                action = event['body-json']['type'].replace(':', '_')
            else:
                action = 'undefined'

        if action == 'answer':
            nexmodata = event['params']['querystring']
        else:
            nexmodata = event['body-json']

        function = direction + "_" + action
        debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno, 
                "function=%s data=%s" % (function, nexmodata))

        func = ch.get(function)
        if func is not None:
            response = func(nexmodata)
        else:
            response = inbound_undefined(nexmodata)

    except KeyError as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "ERROR: Invalid Key %s" % e.args[0])
        response = {}
    except Exception as e:
        error(e.args[0], e.args[1], e.args[3])
        response = {}
    finally:
        debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno, 
                "out = %s" % json.dumps(response))
        return response

#########################
# Inbound Handler
#########################

def inbound_sip_hangup(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    if(nexmodata['body']['direction'] == 'outbound'):
        try:
            caller_uuid = db.Table(config['outboundCallTable']).get_item(
                Key={ 'uuid': nexmodata['body']['channel']['id']})['Item']['caller_uuid']

            p = bytearray()
            p.extend(json.dumps({
                "nexmoKey": config['nexmoKey'],
                "nexmoAppID": config['nexmoAppID'],
                "method": "update_call",
                "uuid": caller_uuid,
                "kwargs": {
                    "action": "hangup"
                    }
                }))
            client = boto3.client('lambda')
            response = client.invoke(
                FunctionName='LambdaNexmo',
                InvocationType='RequestResponse',
                Payload=p
                )
        except Exception as e:
            error(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno, 
                "Unknown error. %s" % e.args[0])
    return {}

# Function will onlly log
def inbound_ringing(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(event))
    return {}

# Function will onlly log
def inbound_started(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(event))
    return {}

# Function will onlly log
def inbound_dtmf(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    return {}

def inbound_undefined(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    return {}

def inbound_answer(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    return [
        { 
            "action": "stream",
            "streamUrl": [ config['silence1s'] ]
        },
        {
            "action": "talk",
            "text": config['customerHello']
        },
        {
            "action": "record",
            "eventUrl": [
                app_url + "/recording/inbound"
            ],
            "endOnSilence": 3,
            "endOnKey": "#",
            "beepStart": "true"
        },
        {
            "action": "talk",
            "text": config['customerWelcome']
        },
        {
            "action": "conversation",
            "name": "samana-support",
            "startOnEnter": "false",
            "musicOnHoldUrl": [ config['moh'] ]
        }
    ]

def inbound_answered(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))

    try:
        agent_data = get_phones()
        db_register_inbound(nexmodata, agent_data)
        db_addcall_queue(nexmodata['uuid'], nexmodata['from'], nexmodata['conversation_uuid'])
    
        t = datetime.utcnow().strftime('%s')
        name = "AgentCall%s" % str(t)
        
        debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno,
                "name=%s" % name)
    
        client = boto3.client('stepfunctions')
        response = client.start_execution(
            stateMachineArn='arn:aws:states:us-east-1:438136544486:stateMachine:CallAgentStateMachine-xO59mMQjDs4y',
            name=name,
            input='{}'
        )
        debug(sys._getframe().f_code.co_name, 
                sys._getframe().f_lineno, 
                "StepFunction started %s" % str(response))
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "Unknown error. %s" % e.args[0])

    return {}

def inbound_completed(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))

    db_complete_inbound(nexmodata)
    db_remcall_queue(nexmodata['uuid'])
    return {}

def inbound_recording(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    try:
        out = db.Table("InboundQueue").scan()
        if out['Count'] == 0: 
            debug(sys._getframe().f_code.co_name, 
                    sys._getframe().f_lineno, 
                    "No calls on queue")
            return {}
        
        for i in out['Items']:
            db.Table("InboundQueue").update_item(
                Key={ "uuid": i['uuid'] },
                UpdateExpression         = "set #s = :s",
                ExpressionAttributeValues= { ":s": nexmodata['recording_url'] },
                ExpressionAttributeNames = { "#s": "recording_url" },
                ReturnValues             = "UPDATED_NEW")

    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "%s %s" % (type(e).__name__, e.args[0]))
        
    return {}
    

#########################
# Outbound Handler
#########################

# Function will onlly log
def outbound_started(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    return {}

# Function will onlly log
def outbound_machine(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    return {}

# Function will onlly log
def outbound_ringing(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    return {}

def outbound_answer(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))

    return [
        { 
            "action": "stream",
            "streamUrl": [ config['silence1s'] ]
        },
        {
            "action": "talk",
            "text": config['agentWelcome']
        },
        {
            "action": "talk",
            "text": config['agentPlaceIntoConf']
        },
        {
            "action": "conversation",
            "name": "samana-support",
            "startOnEnter": True
        }#,
#        {
#            "action": "talk",
#            "text": config['agentAccept'],
#            "bargeIn": True
#        },
#        {
#            "action": "input",
#            "maxDigits": 1,
#            "eventUrl": [ app_url + "/dtmf/outbound" ]
#        }
        ]

def outbound_dtmf(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))

    if nexmodata['timed_out']:
        warn(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "dtmf timeout")
        db_update_outbound(nexmodata, 'rejected', False)
        response = {}
    else:
        db_connect_inbound(nexmodata)
        response = [
            {
                "action": "talk",
                "text": config['agentPlaceIntoConf']
            },
            {
                "action": "conversation",
                "name": "samana-support",
                "startOnEnter": True
            }]

    return response

def outbound_human(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    db_connect_inbound(nexmodata)
    return {}

def outbound_answered(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    try:
        db.Table("AgentCalls").update_item(
            Key                      = { "uuid": nexmodata['uuid'] },
            UpdateExpression         = "set #s = :s",
            ExpressionAttributeValues= { ":s": nexmodata['status'] },
            ExpressionAttributeNames = { "#s": "status" },
            ReturnValues             = "UPDATED_NEW")
        response = {}

    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to update AgentCalls table. %s" % e.args[0])
        response = {}

    finally:
        return response

def outbound_completed(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    try:
        table = db.Table("AgentCalls")
        response = {}
        status = "completed"
        db_remcall_outqueue(nexmodata['uuid'])

        ue = "set #d = :d"
        eav = { ":d": nexmodata['duration'] }
        ean = { "#d": "duration" }
        if "start_time" in nexmodata and nexmodata['start_time'] is not None:
            ue = ue + ", #st = :st"
            eav[':st'] = nexmodata['start_time']
            ean['#st'] = "start_time"
        if "end_time" in nexmodata and nexmodata['end_time'] is not None:
            ue = ue + ", #et = :et"
            eav[':et'] = nexmodata['end_time']
            ean['#et'] = "end_time"
        if status is not None:
            ue = ue + ", #s = :s"
            eav[":s"] = status
            ean["#s"]  = "status"

        table.update_item(
            Key                      = { "uuid": nexmodata['uuid'] },
            UpdateExpression         = ue,
            ExpressionAttributeValues= eav,
            ExpressionAttributeNames = ean,
            ReturnValues             = "UPDATED_NEW")

    except KeyError as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Invalid key. %s" % e.args[0])
        response = {}

    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to update AgentCalls table. %s" % e.args[0])
    finally:
        return response

def outbound_timeout(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    db_update_outbound(nexmodata, 'failed', False)
    db_remcall_outqueue(nexmodata['uuid'])
    return {}

def outbound_failed(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    db_update_outbound(nexmodata, 'failed', False)
    db_remcall_outqueue(nexmodata['uuid'])
    return {}

def outbound_rejected(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    db_update_outbound(nexmodata, 'rejected', False)
    db_remcall_outqueue(nexmodata['uuid'])
    return {}

def outbound_unanswered(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    db_update_outbound(nexmodata, 'unanswered', False)
    db_remcall_outqueue(nexmodata['uuid'])
    return {}

def outbound_busy(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            json.dumps(nexmodata))
    db_update_outbound(nexmodata, 'busy', False)
    db_remcall_outqueue(nexmodata['uuid'])
    return {}

def get_phones():
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName='iTopNexmoCallAgent-ITopNexmoOnCallPhonesFunction-1HI8ELO7A5B1E',
            InvocationType='RequestResponse')
        # TODO implement
        out = json.loads(response['Payload'].read())

    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to update AgentCalls table. %s" % e.args[0])
        out = {}
    return out

def db_addcall_queue(uuid, inbound_phone, conversation_uuid):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        db.Table(config['InboundQueueTable']).put_item(Item={
            "uuid": uuid,
            "from": inbound_phone,
            "conversation_uuid": conversation_uuid
        })
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to register call into Queue. %s" % e.args[0])

def db_remcall_queue(uuid):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        db.Table(config['InboundQueueTable']).delete_item(
            Key={ "uuid": uuid }
            )
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to delete call from InboundQueue. %s" % e.args[0])

def db_remcall_outqueue(uuid):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        db.Table(config['outboundQueueTable']).delete_item(
            Key={ "uuid": uuid }
            )
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to delete call from OutboundQueue. %s" % e.args[0])

def db_register_inbound(nexmodata, agent_data):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        db.Table(config['InboundCallTable']).put_item(Item={
            "uuid": nexmodata['uuid'],
            "direction": nexmodata['direction'],
            "conversation_uuid": nexmodata['conversation_uuid'],
            "answered": False,
            "to": nexmodata['to'],
            "from": nexmodata['from'],
            "status": 'waiting',
            "timestamp": nexmodata['timestamp'],
            "agent_data": agent_data
        })
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to register call into SamanaNexmo. %s" % e.args[0])

def db_complete_inbound(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        db.Table(config['InboundCallTable']).update_item(
            Key={ "uuid": nexmodata['uuid'] },
            UpdateExpression="set #d = :duration, start_time = :st, end_time = :et, rate = :r, price = :p, #s = :s",
            ExpressionAttributeValues={ 
                ":duration": nexmodata['duration'],
                ":st": nexmodata['start_time'],
                ":et": nexmodata['end_time'],
                ":r": nexmodata['rate'],
                ":p": nexmodata['price'],
                ":s": nexmodata['status']
            },
            ExpressionAttributeNames= { "#s": "status", "#d": "duration" },
            ReturnValues="UPDATED_NEW")
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to register call into SamanaNexmo. %s" % e.args[0])

def db_connect_inbound(nexmodata):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        caller_uuid = db.Table(config['outboundCallTable']).get_item(
            Key={ 'uuid': nexmodata['call_uuid']})['Item']['caller_uuid']
        db.Table(config['InboundCallTable']).update_item(
            Key                      = { "uuid": caller_uuid },
            UpdateExpression         = "set #a = :a, #s = :s",
            ExpressionAttributeValues= {
                ":a": True,
                ":s": "incall"
                },
            ExpressionAttributeNames = { 
                "#a": "answered",
                "#s": "status"
                },
            ReturnValues="UPDATED_NEW")
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to update inbound call. %s" % e.args[0])

def db_register_outbound(agent_call_data, phones):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        table = db.Table(config['outboundCallTable'])
        newcall_data = table.put_item(Item={
            "uuid": agent_call_data['uuid'],
            "caller_uuid": caller_data['uuid'],
            "direction": agent_call_data['direction'],
            "conversation_uuid": agent_call_data['conversation_uuid'],
            "status": agent_call_data['status'],
            "phones": phones
        });
        debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "newcall_data: %s" % json.dumps(newcall_data))

    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to register outbound call. %s" % e.args[0])

def db_update_outbound(nexmodata, status, answered):
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        out = db.Table(config['outboundCallTable']).update_item(
            Key                      = { 
                "uuid": nexmodata['uuid'] 
            },
            UpdateExpression         = "set #s = :s",
            ExpressionAttributeValues= {
                ":s": status
                },
            ExpressionAttributeNames = { 
                "#s": "status"
                },
            ReturnValues="UPDATED_NEW")

    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to update outbound call. %s" % e.args[0])
        out = {}

    return out

def db_error_outbound():
    debug(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno, 
            "start")
    try:
        table = db.Table(config['outboundCallTable'])
        table.update_item(
            Key                      = { "uuid": event['uuid'] },
            UpdateExpression         = "set #p = :p",
            ExpressionAttributeValues={ 
                ":p": "Unknown Error"
                },
            ExpressionAttributeNames = { 
                "#p": "agent_phones"
                },
            ReturnValues="UPDATED_NEW")
    except Exception as e:
        error(sys._getframe().f_code.co_name, 
            sys._getframe().f_lineno,
            "Unable to update outbound call. %s" % e.args[0])

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

ch = {
    'inbound_answer'     : inbound_answer,
    'inbound_ringing'    : inbound_ringing,
    'inbound_started'    : inbound_started,
    'inbound_answered'   : inbound_answered,
    'inbound_completed'  : inbound_completed,
    'inbound_recording'  : inbound_recording,
    'inbound_undefined'  : inbound_undefined,
    'inbound_sip_hangup' : inbound_sip_hangup,
    'outbound_answer'    : outbound_answer,
    'outbound_started'   : outbound_started,
    'outbound_ringing'   : outbound_ringing,
    'outbound_answered'  : outbound_answered,
    'outbound_machine'   : outbound_machine,
    'outbound_completed' : outbound_completed,
    'outbound_timeout'   : outbound_timeout,
    'outbound_failed'    : outbound_failed,
    'outbound_rejected'  : outbound_rejected,
    'outbound_unanswered': outbound_unanswered,
    'outbound_busy'      : outbound_busy,
    'outbound_dtmf'      : outbound_dtmf,
    'outbound_human'     : outbound_human
}
from datetime import datetime
from random import randint
from uuid import uuid4
