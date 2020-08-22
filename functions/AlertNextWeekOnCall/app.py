import sys
import os
import json
sys.path.insert(0, "./lib")
import boto3
from requests import post
from requests.auth import HTTPBasicAuth
import urllib.parse

config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')
config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']

def handler(event, context):
    client_id     = os.environ['client_id']
    client_secret = os.environ['client_secret']
    s_app_id      = int(os.environ['s_app_id']) # Staffing app
    s_app_token   = os.environ['s_app_token']   # Staffing token

    if not has_missing_oncall():
        return {}

    emails = get_emails()
    if len(emails) < 1: 
        print("ERROR: Cannot get SDMs emails for alert")
        return {}
    
    if int(t['filtered']) < 1:
        res = send_email(emails)
    else:
        res = {}

    return res

def has_missing_oncall():
    itop_ip     = config['itop_ip']
    itop_user   = config['itop_user']
    itop_pw     = config['itop_pw']

    itop_rest_version = "1.3"
    # TODO: change range for 4 days
    json_data = {
        "operation":"core/get",
        "class":"OnCall",
        "key":"SELECT OnCall "\
            "WHERE day > DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00') "\
            "AND day < DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 1 MONTH),'%Y-%m-%d 00:00:00')",
        "output_fields":"primary_external_id,backup_external_id,manager_external_id"
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

    if len(jsonRes.get('objects')) < 3:
        print(len(jsonRes.get('objects')))
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
        'key':'SELECT User ' \
        + 'JOIN URP_UserProfile ON URP_UserProfile.userid = User.id '\
        + 'WHERE URP_UserProfile.profileid={}'.format(oncall_scheduler_profileid),
        'output_fields':'email'
    }

    query_str = urllib.parse.urlencode({
        'version': itop_rest_version, 
        'json_data': json.dumps(json_data)
    })

    res = post(
        'http://' + itop_ip + '/itop/webservices/rest.php?' + query_str, 
        auth=HTTPBasicAuth(itop_user, itop_pw),
    )
    jsonRes = res.json()

    return [val.get('fields').get('email') \
        for key,val in  jsonRes.get('objects').items()]

def send_email(emails):
    client = boto3.client('ses')
    
    message = """
Hello, this is a message from Samana\'s Phone System.

You are receiving this message, because next week there is no assignment
for OnCall. This means that in a few days the system will not be able
to accept calls, because no agents will be available.

Please access iTop and assign a resource to OnCall for next week.

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
