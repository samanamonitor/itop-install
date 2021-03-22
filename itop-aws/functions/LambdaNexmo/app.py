import sys
sys.path.insert(0, "./lib")
import vonage
import json

def handler(event, context):
    print("DEBUG: %s" % (json.dumps(event)))
    private_key = event.get('nexmoKey')
    if private_key is None: 
        print("Private Key Missing.")
        return {}
    #private_key = '\n'.join(private_key.split('\\n'))

    application_id = event.get('nexmoAppID')
    if application_id is None: 
        print("Application ID Missing.")
        return {}

    method = event.get('method')
    if method is None:
        print("Method Missing")
        return {}

    uuid = event.get('uuid')

    kwargs = event.get('kwargs')

    client = vonage.Client(application_id=application_id, private_key=private_key)
    m = getattr(client, method)
    if m is None:
        print("Invalid Method")
        return {}
    if uuid is not None:
        if kwargs is None:
            return m(uuid)
        else:
            return m(uuid, kwargs)
    elif kwargs is None:
        return m()
    else:
        print(json.dumps(kwargs, indent=2))
        return m(kwargs)
