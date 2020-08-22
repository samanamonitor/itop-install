from functions.AlertNextWeekOnCall import app
from requests_mock import Mocker

def test_has_missing_oncall(monkeypatch):
    monkeypatch.setenv('itop_ip', '127.0.0.1', prepend=False)
    monkeypatch.setenv('itop_user', 'testUser', prepend=False)
    monkeypatch.setenv('itop_pw', 'pw123', prepend=False)

    with Mocker() as m:
        m.post(
            'http://127.0.0.1/itop/webservices/rest.php?'+\
                'version=1.3&json_data=%7B%22operation%22%3A'+\
                '+%22core%2Fget%22%2C+%22class%22%3A+%22OnCall'+\
                '%22%2C+%22key%22%3A+%22SELECT+OnCall+WHERE+day'+\
                '+%3E+DATE_FORMAT%28NOW%28%29%2C%27%25Y-%25m-%25d+'+\
                '00%3A00%3A00%27%29+AND+day+%3C+DATE_FORMAT%28'+\
                'DATE_ADD%28NOW%28%29%2C+INTERVAL+1+MONTH'+\
                '%29%2C%27%25Y-%25m-%25d+00%3A00%3A00%27%29%22%2C'+\
                '+%22output_fields%22%3A+%22primary_external_id%2C'+\
                'backup_external_id%2Cmanager_external_id%22%7D', 
            json={
                "objects": {
                    "OnCall::3": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "3",
                        "fields": {
                            "primary_external_id": "9",
                            "backup_external_id": "15",
                            "manager_external_id": "4"
                        }
                    },
                    "OnCall::4": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "4",
                        "fields": {
                            "primary_external_id": "9",
                            "backup_external_id": "15",
                            "manager_external_id": "4"
                        }
                    },
                    "OnCall::5": {
                        "code": 0,
                        "message": "",
                        "class": "OnCall",
                        "key": "5",
                        "fields": {
                            "primary_external_id": "9",
                            "backup_external_id": "15",
                            "manager_external_id": "4"
                        }
                    }
                },
                "code": 0,
                "message": "Found: 3"
            }
        )

        assert app.has_missing_oncall() == False

def test_get_emails(monkeypatch):
    monkeypatch.setenv('itop_ip', '127.0.0.1', prepend=False)
    monkeypatch.setenv('itop_user', 'testUser', prepend=False)
    monkeypatch.setenv('itop_pw', 'pw123', prepend=False)

    with Mocker() as m:
        m.post(
            'http://127.0.0.1/itop/webservices/rest.php?' +\
                'version=1.3&json_data=%7B%22operation%22%3A+'+\
                '%22core%2Fget%22%2C+%22class%22%3A+%22User%22%'+\
                '2C+%22key%22%3A+%22SELECT+User+JOIN+URP_UserProfile'+\
                '+ON+URP_UserProfile.userid+%3D+User.id+'+\
                'WHERE+URP_UserProfile.profileid%3D50%22%2C'+\
                '+%22output_fields%22%3A+%22email%22%7D', 
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