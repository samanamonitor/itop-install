import sys
sys.path.insert(0, "./lib")
import os
import jwt
from datetime import datetime
import calendar
from base64 import urlsafe_b64encode

def handler(event, context) :

    application_id=event['application_id']
    application_private_key    = '\n'.join(event['application_private_key'].split('\\n'))

    # Add the unix time at UCT + 0
    d = datetime.utcnow()

    token_payload = {
        "iat": calendar.timegm(d.utctimetuple()),  # issued at
         "application_id": application_id,  # application id
         "jti": urlsafe_b64encode(os.urandom(64)).decode('utf-8')
    }

    # generate our token signed with this private key...
    return { "data": jwt.encode(
        payload=token_payload,
        key=application_private_key,
        algorithm='RS256') }

if __name__ == "__main__":
    event = {
        'application_id': sys.argv[1],
        'application_private_key': sys.argv[2]
    }
    a = handler(event, {})
    print(a)