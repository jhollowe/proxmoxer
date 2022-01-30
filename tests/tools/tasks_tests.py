from nose.tools import eq_

from proxmoxer.tools.tasks import Tasks


def test_decode_upic_password():
    upid = "UPID:test-node:0012CC24:00DBE72B:61BF08F5:aptupdate::root@pam:"
    expected = {
        "node": "test-node",
        "pid": 1231908,
        "pstart": 14411563,
        "starttime": 1639909621,
        "type": "aptupdate",
        "id": "",
        "user": "root@pam",
    }

    t = Tasks(None)

    eq_(t.decode_upid(upid), expected)


def test_decode_upic_apitoken():
    upid = "UPID:test-node:0012CC24:00DBE72B:61BF08F5:aptupdate::root@pam!test_token:"
    expected = {
        "node": "test-node",
        "pid": 1231908,
        "pstart": 14411563,
        "starttime": 1639909621,
        "type": "aptupdate",
        "id": "",
        "user": "root@pam",
    }

    t = Tasks(None)

    eq_(t.decode_upid(upid), expected)


def test_decode_log_empty():
    in_log = []
    expected_log = ""

    t = Tasks(None)

    eq_(t.decode_log(in_log), expected_log)


def test_decode_log_ordered():
    in_log = [{"n": 1, "t": "a"}, {"n": 2, "t": "b"}, {"n": 3, "t": "c"}]
    expected_log = "a\nb\nc"

    t = Tasks(None)

    eq_(t.decode_log(in_log), expected_log)


def test_decode_log_unordered():
    in_log = [{"n": 3, "t": "c"}, {"n": 1, "t": "a"}, {"n": 2, "t": "b"}]
    expected_log = "a\nb\nc"

    t = Tasks(None)

    eq_(t.decode_log(in_log), expected_log)


def test_decode_log_single():
    in_log = [{"n": 1, "t": "TASK OK"}]
    expected_log = "TASK OK"

    t = Tasks(None)

    eq_(t.decode_log(in_log), expected_log)
