import json
from unittest.mock import patch

from sqlite_testdb import SqliteTest


class TestSbsCommentApi(SqliteTest):
    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_get_request_comments(self, test_patch):
        """
        Tests if expected comments are returned for particular request
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        actual_json = self.client.get('/sbs/requests/AA200/comments')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual(1, actual_json['data'][0]['request_id'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_get_request_comments_with_incorrect_request_id(self, test_patch):
        """
        Tests if empty list is returned for incorrect request id
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        actual_json = self.client.get('/sbs/requests/1/comments')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual([], actual_json['data'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_get_sample_comments(self, test_patch):
        """
        Tests if expected comments are returned for particular sample
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        actual_json = self.client.get('/sbs/analyses/1/comments')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual(1, actual_json['data'][0]['analysis_id'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_add_request_comment(self, test_patch):
        """
        Test if comment for particular request is added successfully
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        request_data = json.dumps(dict(comment="comment"))
        actual_json = self.client.post('/sbs/requests/AA200/comments',
                                       data=request_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        assert 'Successfully added comment for request' in actual_json['data']

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_add_request_comment_with_incorrect_request_id(self, test_patch):
        """
        Test if comment is not added for incorrect request_id
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        request_data = json.dumps(dict(comment="comment"))
        actual_json = self.client.post('/sbs/requests/10/comments',
                                       data=request_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Error', actual_json['status']['message'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_add_sample_comment(self, test_patch):
        """
        Test if comment for particular sample is added successfully
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        request_data = json.dumps(dict(comment="comment"))
        actual_json = self.client.post('/sbs/analyses/1/comments',
                                       data=request_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        assert 'Successfully added comment for analysis' in actual_json['data']

    def test_get_observed_map_comments(self):
        """
        Tests if expected comments are returned for particular sample
        """
        actual_json = self.client.get('/sbs/observed_maps/1/comments')
        actual_json = json.loads(actual_json.data)
        self.assertEqual(1, actual_json['data'][0]['observed_map_id'])
        self.assertEqual('Success', actual_json['status']['message'])

    def test_get_observed_map_comments_with_incorrect_id(self):
        """
        Tests if expected comments are returned for particular sample
        """
        actual_json = self.client.get('/sbs/observed_maps/1a/comments')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual([], actual_json['data'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_add_observed_map_comment(self, test_patch):
        """
        Test if comment for particular sample is added successfully
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        request_data = json.dumps(dict(comment="comment"))
        actual_json = self.client.post('/sbs/observed_maps/1/comments',
                                       data=request_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
