from requests_mock import Mocker

def test_has_missing_oncall(monkeypatch):
    monkeypatch.setenv('config_table', 'iTopNexmoPhoneConfig', prepend=False)
    
    from functions.AlertNextWeekOnCall import app
    
    monkeypatch.setenv('itop_ip', '127.0.0.1', prepend=False)
    monkeypatch.setenv('itop_user', 'testUser', prepend=False)
    monkeypatch.setenv('itop_pw', 'pw123', prepend=False)

    with Mocker() as m:
        m.post(
            'http://127.0.0.1/itop/webservices/rest.php', 
            json={
                "objects": {
                    "OnCall::14": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "14",
                        "fields": {
                            "type": "Primary",
                            "number": "",
                            "email": ""
                        }
                    },
                    "OnCall::16": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "16",
                        "fields": {
                            "type": "Primary",
                            "number": "",
                            "email": ""
                        }
                    },
                    "OnCall::17": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "17",
                        "fields": {
                            "type": "Primary",
                            "number": "3054239153",
                            "email": "andres.cubas@samanagroup.co"
                        }
                    },
                    "OnCall::18": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "18",
                        "fields": {
                            "type": "Backup",
                            "number": "5555555556",
                            "email": "andres.cubas@samanagroup.co"
                        }
                    }
                },
                "code": 0,
                "message": "Found: 4"
            }
        )

        assert app.has_missing_oncall() == True

def test_get_emails(monkeypatch):

    monkeypatch.setenv('config_table', 'iTopNexmoPhoneConfig', prepend=False)
    
    from functions.AlertNextWeekOnCall import app

    monkeypatch.setenv('itop_ip', '127.0.0.1', prepend=False)
    monkeypatch.setenv('itop_user', 'testUser', prepend=False)
    monkeypatch.setenv('itop_pw', 'pw123', prepend=False)

    with Mocker() as m:
        m.post(
            'http://127.0.0.1/itop/webservices/rest.php', 
            json={
                "objects": {
                    "UserLocal::14": {
                        "code": 0,
                        "message": "",
                        "class": "UserLocal",
                        "key": "14",
                        "fields": {
                            "email": "email1@domain.com"
                        }
                    },
                    "UserLocal::15": {
                        "code": 0,
                        "message": "",
                        "class": "UserLocal",
                        "key": "15",
                        "fields": {
                            "email": "email2@domain.com"
                        }
                    }
                },
                "code": 0,
                "message": "Found: 2"
            }
        )
        
        emails = app.get_emails()
        assert len(emails) == 2
        assert emails[0] == 'email1@domain.com'
        assert emails[1] == 'email2@domain.com'