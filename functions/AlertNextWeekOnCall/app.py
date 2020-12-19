import sys
import os
import json
sys.path.insert(0, "./lib")
import boto3
from requests import post
import urllib.parse

config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')
config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

def handler(event, context):

    if not has_missing_oncall():
        return {}

    emails = get_emails()
    if len(emails) < 1: 
        print("ERROR: Cannot get SDMs emails for alert")
        return {}
    
    
    res = send_email(emails)

    return res

def has_missing_oncall():
    itop_ip     = config['itop_ip']
    itop_user   = config['itop_user']
    itop_pw     = config['itop_pw']

    itop_rest_version = "1.3"
    json_data = {
        "operation":"core/get",
        "class":"OnCall",
        "key":"SELECT OnCall "
        "WHERE (day > DATE_FORMAT(NOW(),'%Y-%m-%d') AND day <= DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 5 DAY),'%Y-%m-%d') ) "
        "OR (repeat_until_end_of > DATE_FORMAT(NOW(),'%Y-%m-%d') AND repeat_until_end_of <= DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 5 DAY),'%Y-%m-%d') )",
        "output_fields":"type,number,email"
    }

    data = {
        'version': itop_rest_version, 
        'json_data': json.dumps(json_data),
        'auth_user': itop_user,
        'auth_pwd': itop_pw
    }

    res = post(
        'http://' + itop_ip + '/itop/webservices/rest.php',
        data=data
    )
    jsonRes = res.json()

    if jsonRes.get('objects') is None or len(jsonRes.get('objects')) < 3:
        return True

    # Check if there is a primary, backup and manager
    scheduledRoles = { val['fields']['type'] for key,val in jsonRes.get('objects').items() }
    if len(scheduledRoles) < 3 or ('' in scheduledRoles and scheduledRoles < 4):
        return True

    for key,val in jsonRes.get('objects').items():
        if len(val.get('fields')) < 3:
            return True

    return False


def get_emails():

    itop_ip     = config['itop_ip']
    itop_user   = config['itop_user']
    itop_pw     = config['itop_pw']

    oncall_scheduler_profileid = 50
    itop_rest_version = "1.3"
    json_data = {
        'operation':'core/get',
        'class':'User',
        'key':'SELECT User '
        'JOIN URP_UserProfile ON URP_UserProfile.userid = User.id '
        'WHERE URP_UserProfile.profileid=50'.format(oncall_scheduler_profileid),
        'output_fields':'email'
    }

    data = {
        'version': itop_rest_version, 
        'json_data': json.dumps(json_data),
        'auth_user': itop_user,
        'auth_pwd': itop_pw
    }

    res = post(
        'http://' + itop_ip + '/itop/webservices/rest.php',
        data=data
    )
    jsonRes = res.json()

    return [val.get('fields').get('email') \
        for key,val in  jsonRes.get('objects').items()]

def send_email(emails):
    client = boto3.client('ses')
    
    message = """
Hello, this is a message from Samana\'s Phone System.

You are receiving this message, because for the next four days there is no assignment
for OnCall. This means that in a few days the system will not be able
to accept calls, because no agents will be available.

Please access iTop and assign a resource to OnCall for the next four days.

If you don't do this whithin the next 24 hours, you'll get this meesage 
again.

Thank you

Samana's Phone System

"""
    
    response = client.send_email(
        Source='phonesystem@samanagroup.com',
        Destination={
            'ToAddresses': emails
        },
        Message={
            'Subject': {
                'Data': 'ALERT!! OnCall assignment for next week not configured',
                'Charset': 'utf8'
            },
            'Body': {
                'Text': {
                    'Data': message,
                    'Charset': 'utf8'
                }
            }
        }
    )
    return response
