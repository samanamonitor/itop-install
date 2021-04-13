from requests import Session
from urllib.parse import urlencode
import xml.etree.ElementTree as ET


class AstManagerServerError(Exception):
    pass

class AstManager:
    def __init__(self, username, secret, host='localhost', port='8088', protocol='http', prefix=''):
        self.session = Session()
        self.username = username
        self.secret = secret
        self.host = host
        self.port = port
        self.protocol = protocol
        self.prefix=prefix
        self.login()
    def _request(self, data):
        qs = urlencode(data)
        res = s.get('%s://%s:%s%s/mxml?%s' % 
            (self.protocol, self.host, self.port, self.prefix, qs))
        self.status_code=res.status_code
        if self.status_code != 200:
            raise AstManagerServerError("Server returned status %s" % self.status_code)
        self._content = res.content.decode('ascii')
        self._xml_root = ET.fromstring(self._content)
        if self._xml_root.tag != 'ajax-response':
            raise AstManagerServerError("XML root tag should be 'ajax-response' but received '%s'" % \
                self._xml_root.tag)
        self._events = []
        self._objects = []
        for o in self._xml_root.findall(".//generic"):
            obj = o.attrib
            if 'response' in obj:
                self._response = obj
            elif 'event' in obj:
                self._events += [ obj ]
            else:
                self._objects += [ obj ]
        if self._response['response'].lower() == 'error':
            raise AstManagerServerError(self._response['message'])
    def login(self):
        self._request({
            'action': 'login',
            'username': self.username,
            'secret': self.secret
            })
    def add_member(self, queue, interface):
        self._request({
            'action': 'QueueAdd',
            'Queue': queue,
            'Interface': interface
            })
    def remove_member(self, queue, interface):
        self._request({
            'action': 'QueueRemove',
            'Queue': queue,
            'Interface': interface
            })
    def get_queue_members(self, queue):
        res = self._request({
            'action': 'QueueStatus',
            'Queue': queue
            })
        _qmembers = []
        for event in self._events: #  self._xml_root.findall(".//*[@event='QueueMember']"):
            if event['event'] == 'QueueMember':
                _qmembers += [event['name'].split('/')[1]]
        return _qmembers
