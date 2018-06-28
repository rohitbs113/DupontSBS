import json
from unittest.mock import patch

from sqlite_testdb import SqliteTest


class TestSbsUserApi(SqliteTest):
    def test_add_user_rest(self):
        user_data = json.dumps(dict(username='unittest1', role='lab',
                                    active='y'))
        actual_json = self.client.post('/sbs/users', data=user_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    def test_update_user_rest(self):
        user_data = json.dumps(dict(active='y'))
        actual_json = self.client.put('/sbs/users/unittest', data=user_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_get_user(self, test_patch1):
        info = {"user_name": "unittest"}
        test_patch1.return_value = info
        actual_result = self.client.get('/sbs/users')
        actual_json = json.loads(actual_result.data)
        self.assertEqual(actual_json['data']['user_name'], 'unittest')
        self.assertEqual(actual_json['data']['role'], 'lab')
        self.assertEqual(actual_json['data']['active'], True)
