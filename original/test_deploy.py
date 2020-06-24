import os
import unittest
from unittest import mock

from .deploy import deploy
from .deploy import is_deployable
from .deploy import is_secure
from .deploy import to_dict

SECRET = 'THIS IS SECRET'


class TestServer(unittest.TestCase):
    def setUp(self):
        self.github_sig = 'sha1=8ce53d8902bcdda20c64dc3ae0ea249e7567d74a'
        self.request_body = 'REQUESTBODY'.encode()

    def test_to_dict(self):
        self.assertTrue(to_dict('{"to": "json"}'))

    def test_to_dict_empty(self):
        self.assertEqual({}, to_dict(''))

    def test_is_deployable_push(self):
        payload_json = {"ref": "refs/heads/master"}
        self.assertTrue(is_deployable(payload_json))

    def test_is_deployable_merge_pr(self):
        payload = {
            "action": "closed",
            "pull_request": {"merged": True, "base": {"ref": "master"}},
        }
        self.assertTrue(is_deployable(payload))

    def test_is_secure(self):
        self.assertTrue(is_secure(self.github_sig, SECRET, self.request_body))

    def test_is_deploy(self):
        payload_str = '''
            {"ref": "refs/heads/master"}
        '''
        deploy(self.github_sig, SECRET, self.request_body, payload_str)
