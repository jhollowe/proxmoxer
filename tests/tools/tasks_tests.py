

from mock import patch, MagicMock
from nose.tools import eq_, ok_, assert_raises
from proxmoxer import ProxmoxAPI
from proxmoxer.tools.tasks import Tasks


@patch('requests.sessions.Session')
def test_upid_decode_password():
  upid = ''
  expected = {}

  prox = ProxmoxAPI('proxmox', user='root@pam', password='secret', port=123, verify_ssl=False)
  t = Tasks(prox)

  eq_(t.decode_upid(upid), expected)
