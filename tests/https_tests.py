__author__ = 'Oleg Butovich'
__copyright__ = '(c) Oleg Butovich 2013-2017'
__licence__ = 'MIT'

from mock import patch, MagicMock
from nose.tools import eq_, ok_, assert_raises
from proxmoxer import ProxmoxAPI


@patch('requests.sessions.Session')
def test_https_connection(req_session):
    response = {'ticket': 'ticket',
                'CSRFPreventionToken': 'CSRFPreventionToken'}
    req_session.request.return_value = response
    ProxmoxAPI('proxmox', user='root@pam', password='secret', port=123, verify_ssl=False)
    call = req_session.return_value.request.call_args[1]
    eq_(call['url'], 'https://proxmox:123/api2/json/access/ticket')
    eq_(call['data'], {'username': 'root@pam', 'password': 'secret'})
    eq_(call['method'], 'post')
    eq_(call['verify'], False)


@patch('requests.sessions.Session')
def test_https_connection_with_port_in_host(req_session):
    response = {'ticket': 'ticket',
                'CSRFPreventionToken': 'CSRFPreventionToken'}
    req_session.request.return_value = response
    ProxmoxAPI('proxmox:123', user='root@pam', password='secret', port=124, verify_ssl=False)
    call = req_session.return_value.request.call_args[1]
    eq_(call['url'], 'https://proxmox:123/api2/json/access/ticket')
    eq_(call['data'], {'username': 'root@pam', 'password': 'secret'})
    eq_(call['method'], 'post')
    eq_(call['verify'], False)


@patch('requests.sessions.Session')
def test_https_connection_with_bad_port_in_host(req_session):
    response = {'ticket': 'ticket',
                'CSRFPreventionToken': 'CSRFPreventionToken'}
    req_session.request.return_value = response
    ProxmoxAPI('proxmox:notaport', user='root@pam', password='secret', port=124, verify_ssl=False)
    call = req_session.return_value.request.call_args[1]
    eq_(call['url'], 'https://proxmox:124/api2/json/access/ticket')
    eq_(call['data'], {'username': 'root@pam', 'password': 'secret'})
    eq_(call['method'], 'post')
    eq_(call['verify'], False)


def test_https_api_token():
    p = ProxmoxAPI('proxmox', user='root@pam', token_name='test', token_value='ab27beeb-9ac4-4df1-aa19-62639f27031e', verify_ssl=False)
    eq_(p.get_tokens()[0], None)
    eq_(p.get_tokens()[1], None)


def test_https_pmg_token():
    with assert_raises(NotImplementedError):
        ProxmoxAPI('proxmox', user='root@pam', token_name='test', token_value='ab27beeb-9ac4-4df1-aa19-62639f27031e', verify_ssl=False, service='PMG')

def test_https_invalid_service():
    with assert_raises(NotImplementedError):
        ProxmoxAPI('nothing', user='root@pam', token_name='test', token_value='ab27beeb-9ac4-4df1-aa19-62639f27031e', verify_ssl=False, service='asdf')


@patch('requests.sessions.Session')
def test_pbs_https_connection(req_session):
    response = {'ticket': 'ticket',
                'CSRFPreventionToken': 'CSRFPreventionToken'}
    req_session.request.return_value = response
    ProxmoxAPI('proxmox', user='root@pam', password='secret', verify_ssl=False, service='pbs')
    call = req_session.return_value.request.call_args[1]
    eq_(call['url'], 'https://proxmox:8007/api2/json/access/ticket')
    eq_(call['data'], {'username': 'root@pam', 'password': 'secret'})
    eq_(call['method'], 'post')
    eq_(call['verify'], False)


class TestSuite():
    proxmox = None
    serializer = None
    session = None

    # noinspection PyMethodOverriding
    @patch('requests.sessions.Session')
    def setUp(self, session):
        response = {'ticket': 'ticket',
                    'CSRFPreventionToken': 'CSRFPreventionToken'}
        session.request.return_value = response
        self.proxmox = ProxmoxAPI('proxmox', user='root@pam', password='secret', port=123, verify_ssl=False)
        self.serializer = MagicMock()
        self.session = MagicMock()
        self.session.request.return_value.status_code = 200
        self.proxmox._store['session'] = self.session
        self.proxmox._store['serializer'] = self.serializer

    def test_get(self):
        self.proxmox.nodes('proxmox').storage('local').get()
        eq_(self.session.request.call_args[0], ('GET', 'https://proxmox:123/api2/json/nodes/proxmox/storage/local'))

    def test_delete(self):
        self.proxmox.nodes('proxmox').openvz(100).delete()
        eq_(self.session.request.call_args[0], ('DELETE', 'https://proxmox:123/api2/json/nodes/proxmox/openvz/100'))
        self.proxmox.nodes('proxmox').openvz('101').delete()
        eq_(self.session.request.call_args[0], ('DELETE', 'https://proxmox:123/api2/json/nodes/proxmox/openvz/101'))

    def test_post(self):
        node = self.proxmox.nodes('proxmox')
        node.openvz.create(vmid=800,
                           ostemplate='local:vztmpl/debian-6-turnkey-core_12.0-1_i386.tar.gz',
                           hostname='test',
                           storage='local',
                           memory=512,
                           swap=512,
                           cpus=1,
                           disk=4,
                           password='secret',
                           ip_address='10.0.100.222')
        eq_(self.session.request.call_args[0], ('POST', 'https://proxmox:123/api2/json/nodes/proxmox/openvz'))
        ok_('data' in self.session.request.call_args[1])
        data = self.session.request.call_args[1]['data']
        eq_(data['cpus'], 1)
        eq_(data['disk'], 4)
        eq_(data['hostname'], 'test')
        eq_(data['ip_address'], '10.0.100.222')
        eq_(data['memory'], 512)
        eq_(data['ostemplate'], 'local:vztmpl/debian-6-turnkey-core_12.0-1_i386.tar.gz')
        eq_(data['password'], 'secret')
        eq_(data['storage'], 'local')
        eq_(data['swap'], 512)
        eq_(data['vmid'], 800)

        node = self.proxmox.nodes('proxmox1')
        node.openvz.post(vmid=900,
                         ostemplate='local:vztmpl/debian-7-turnkey-core_12.0-1_i386.tar.gz',
                         hostname='test1',
                         storage='local1',
                         memory=1024,
                         swap=1024,
                         cpus=2,
                         disk=8,
                         password='secret1',
                         ip_address='10.0.100.111')
        eq_(self.session.request.call_args[0], ('POST', 'https://proxmox:123/api2/json/nodes/proxmox1/openvz'))
        ok_('data' in self.session.request.call_args[1])
        data = self.session.request.call_args[1]['data']
        eq_(data['cpus'], 2)
        eq_(data['disk'], 8)
        eq_(data['hostname'], 'test1')
        eq_(data['ip_address'], '10.0.100.111')
        eq_(data['memory'], 1024)
        eq_(data['ostemplate'], 'local:vztmpl/debian-7-turnkey-core_12.0-1_i386.tar.gz')
        eq_(data['password'], 'secret1')
        eq_(data['storage'], 'local1')
        eq_(data['swap'], 1024)
        eq_(data['vmid'], 900)

    def test_put(self):
        node = self.proxmox.nodes('proxmox')
        node.openvz(101).config.set(cpus=4, memory=1024, ip_address='10.0.100.100', onboot=True)
        eq_(self.session.request.call_args[0], ('PUT', 'https://proxmox:123/api2/json/nodes/proxmox/openvz/101/config'))
        data = self.session.request.call_args[1]['data']
        eq_(data['cpus'], 4)
        eq_(data['memory'], 1024)
        eq_(data['ip_address'], '10.0.100.100')
        eq_(data['onboot'], True)

        node = self.proxmox.nodes('proxmox1')
        node.openvz(102).config.put(cpus=2, memory=512, ip_address='10.0.100.200', onboot=False)
        eq_(self.session.request.call_args[0],
            ('PUT', 'https://proxmox:123/api2/json/nodes/proxmox1/openvz/102/config'))
        data = self.session.request.call_args[1]['data']
        eq_(data['cpus'], 2)
        eq_(data['memory'], 512)
        eq_(data['ip_address'], '10.0.100.200')
        eq_(data['onboot'], False)

    def test_hyphen_replacement(self):
        node = self.proxmox.nodes('proxmox')
        storage = node.storage('local')

        # PVE 7.1-2 download
        storage.download_url(content='iso', url='https://www.proxmox.com/en/downloads?task=callelement&format=raw&item_id=638&element=f85c494b-2b32-4109-b8c1-083cca2b7db6&method=download&args[0]=142b8d6088b033169f802f34ff8bcc97', checksum='f469d2e419328c4b8715544c84f629161cc07024ce26ad63f00bc1b07de265df', checksum_algorithm='sha256')
        eq_(self.session.request.call_args[0],
            ('PUT', 'https://proxmox:123/api2/json/nodes/proxmox/storage/local/download-url'))
        data = self.session.request.call_args[1]['data']
        eq_(data['url'], 'https://www.proxmox.com/en/downloads?task=callelement&format=raw&item_id=638&element=f85c494b-2b32-4109-b8c1-083cca2b7db6&method=download&args[0]=142b8d6088b033169f802f34ff8bcc97')
        eq_(data['content'], 'iso')
        eq_(data['checksum'], 'f469d2e419328c4b8715544c84f629161cc07024ce26ad63f00bc1b07de265df')
        eq_(data['checksum-algorithm'], 'sha256')
