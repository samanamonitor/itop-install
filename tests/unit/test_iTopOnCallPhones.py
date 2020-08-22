from functions.PodioOnCallPhones import app
from requests_mock import Mocker

def test_fetch_oncall_numbers(monkeypatch):
    monkeypatch.setenv('itop_ip', '127.0.0.1', prepend=False)
    monkeypatch.setenv('itop_user', 'testUser', prepend=False)
    monkeypatch.setenv('itop_pw', 'pw123', prepend=False)

    with Mocker() as m:
        m.post(
            'http://127.0.0.1/itop/webservices/rest.php?'+
            'version=1.3&json_data=%7B%22operation%22%3A'+
            '+%22core%2Fget%22%2C+%22class%22%3A+%22OnCall'+
            '%22%2C+%22key%22%3A+%22SELECT+OnCall+WHERE+day+'+
            '%3D+DATE_FORMAT%28NOW%28%29%2C%27%25Y-%25m-%25d'+
            '+00%3A00%3A00%27%29%22%2C+%22output_fields%22%3A+'+
            '%22primary%2Cbackup%2Cmanager%22%7D', 
            json={
                "objects": {
                        "OnCall::5": {
                            "code": 0,
                            "message": "",
                            "class": "OnCall",
                            "key": "5",
                            "fields": {
                                "primary": "5555555555",
                                "backup": "5555555556",
                                "manager": "5555555557"
                            }
                        }
                    },
                "code": 0,
                "message": "Found: 1"
            }
        )

        fields = app.fetch_oncall_numbers()
        assert fields['primary'] == '5555555555'
        assert fields['backup'] == '5555555556'
        assert fields['manager'] == '5555555557'
