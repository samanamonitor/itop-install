import sys
sys.path.insert(0, "./lib")
import boto3
import json
import os
import requests

config_table = os.environ['config_table']
db = boto3.resource('dynamodb', region_name='us-east-1')
config = {}

def lambda_handler(event, context):
    global config
    try:
        config = db.Table(config_table).get_item(Key={ 
                "Key": "Config" 
            })['Item']['Value']
    except Exception as e:
        print("ERROR(lambda_handler): Unknown error. %s %s" \
            % ( type(e).__name__, e.args[0]))

    print("DEBUG(lambda_handler): event = %s" % json.dumps(event))

    out = nexmo_recording(event['body-json'])
    return out

def nexmo_recording(nexmodata):
    print("DEBUG(nexmo_recording): %s" % json.dumps(nexmodata))
    try:
        decoded_request = nexmodata
        #Then extract the information you need
        conversation_uuid = decoded_request['conversation_uuid'] + ".mp3"
        #Retrieve the recording URL from the JSON object sent to eventURL
        recording_url = decoded_request['recording_url']
        #The URL looks like:
        # https://api.nexmo.com/media/download?id=52343cf0-342c-45b3-a23b-ca6ccfe234b0

        #Create your JWT
        application_id = config['nexmoAppID']
        application_private_key = config['nexmoKey']
        jwt = generate_jwt(application_id, application_private_key)
        print("DEBUG(nexmo_recording): jwt generated: %s" % jwt)

        #Add the JWT to your headers
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer {0}".format(jwt)
        }
        #Make a request to recording_url
        response = requests.get( recording_url , headers=headers)
        print("DEBUG(nexmo_recording): response headers from nexmo %s" % response.headers)
        file_path = "/tmp/" + conversation_uuid
        f = open(file_path, "wb")
        f.write(response.content)
        f.close()
        print("DEBUG(nexmo_recording): file_path %s" % file_path)
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(
            Filename=file_path, 
            Bucket='samanaphone', 
            Key=conversation_uuid, 
            ExtraArgs={'ACL': 'public-read'})


    except Exception as e:
        print("ERROR(nexmo_recording): %s %s" % (type(e).__name__, e.args[0]))
        if len(e.args) > 1:
            print("%s" % e.args[1])

    return { "filename": conversation_uuid }

def generate_jwt(application_id="none", application_private_key="none"):
    try:
        data = {
            "application_id": application_id,
            "application_private_key": application_private_key
        }
        client = boto3.client('lambda')
        response = client.invoke(
                FunctionName='generateJWT',
                Payload=json.dumps(data),
                InvocationType='RequestResponse')
        jwt = json.load(response['Payload'])['data']
    except Exception as e:
        print("ERROR(generate_JWT): %s %s" % (type(e).__name__, e.args[0]))

    return jwt

