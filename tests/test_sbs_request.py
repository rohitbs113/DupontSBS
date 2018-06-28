import json
from unittest.mock import patch

from sqlite_testdb import SqliteTest


class TestSbsRequestApi(SqliteTest):
    def test_add_request_rest(self):
        """
        Test if data for particular request is added successfully
        """
        request_data = json.dumps(dict(request_id='AA201', released_on=None,
                                       sbs_internalpipeline_version=
                                       'Sbs_Maize_Agro_v2.2',
                                       request_name='SBS for C3GC1RYNR72',
                                       sample_prep_methods='SbS_Maize_SSI',
                                       tx_method_id=1,
                                       researcher='sbs-researcher',
                                       organism_id=1))
        actual_json = self.client.post('/sbs/requests', data=request_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    @patch('sbs.service.request_service.get_request_by_request_id')
    def test_update_request_rest(self, test_patch):
        """
        Test if data for particular request is updated successfully
        """
        test_patch.return_value = ""
        request_data = json.dumps(dict(sbs_internalpipeline_version=
                                       'Sbs_Maize_Agro_v3.2',
                                       request_name='SBS for C3GC1RYNR73',
                                       sample_prep_methods='SbS_Maize_SSI3',
                                       tx_method_id=1, organism_id=1))
        actual_json = self.client.put('/sbs/requests/AA200', data=request_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        #self.assertEqual('Success', actual_json['status']['message'])

    @patch('sbs.service.request_service.get_request_by_request_id')
    def test_update_request_rest_with_incorrect_id(self, test_patch):
        """
        Test if Error is returned if incorrect request is specified
        """
        test_patch.return_value = ""
        request_data = json.dumps(dict(sbs_internalpipeline_version=
                                       'Sbs_Maize_Agro_v3.2',
                                       request_name='SBS for C3GC1RYNR73',
                                       sample_prep_methods='SbS_Maize_SSI3',
                                       tx_method_id=1, organism_id=1))

        actual_json = self.client.put('/sbs/requests/a', data=request_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Error', actual_json['status']['message'])

    def test_delete_request(self):
        """
        Test if particular request is deleted
        """
        actual_json = self.client.delete('/sbs/requests/AA201',
                                         content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    def test_get_request_with_incorrect_id(self):
        """
        Tests if error returned for request_api
        """
        actual_json = self.client.get('/sbs/requests/a/samples')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual([], actual_json['data']['result'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_get_individual_sample_response(self, test_patch):
        """
        Tests if individual sample page route provides expected results
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        actual_json = self.client.get(
            '/sbs/requests/AA200/samples/AA0171000/analyses/1')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    @patch('flask_oidc.OpenIDConnect.user_getinfo')
    def test_get_individual_sample_response_with_invalid_sample_id(self,
                                                                   test_patch):
        """
        Tests if individual sample page route provides empty results with invalid sample_id
        """
        info = {"user_name": "unittest"}
        test_patch.return_value = info
        actual_json = self.client.get(
            '/sbs/requests/AA200/samples/abc/analyses/1')
        actual_json = json.loads(actual_json.data)
        self.assertEqual({}, actual_json['data'])
