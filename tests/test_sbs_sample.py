import json

from sqlite_testdb import SqliteTest


class TestSbsSampleApi(SqliteTest):
    def test_add_sample_rest(self):
        """
        test case for adding sample
        """
        user_data = json.dumps(
            dict(primary_map='test_data', ev_man_event='test_data',
                 other_maps='test_data',
                 request_id='1', construct_name='test_data',
                 event_id='zm047.032.2.1.2',
                 geno_type='GR2HT',
                 organism='Maize', researcher='test_data',
                 sample_name='999999999',
                 develop_stage='v04',
                 growth_location='', treated='0', sample_id='AA0171009',
                 curr_alpha_analysis='1'))
        actual_json = self.client.post('/sbs/samples', data=user_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    def test_update_user_rest(self):
        """
        test case for updating sample
        """
        user_data = json.dumps(
            dict(primary_map='test_data', ev_man_event='test_data',
                 other_maps='test_data',
                 request_id='AA200', construct_name='test_data',
                 event_id='zm047.032.2.1.2',
                 geno_type='GR2HT',
                 organism='Maize', researcher='test_data',
                 sample_name='123456789',
                 develop_stage='v04',
                 growth_location='', treated='0'))
        actual_json = self.client.put('/sbs/samples/AA0171001', data=user_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        print(json.dumps(actual_json, indent=4))
        self.assertEqual('Success', actual_json['status']['message'])

    def test_delete_sample_rest(self):
        """
        test case for deleting sample
        """
        user_data = json.dumps(
            dict(id='1', primary_map='test_data', ev_man_event='test_data',
                 other_maps='test_data',
                 request_id='4', construct_name='test_data',
                 event_id='zm047.032.2.1.2',
                 geno_type='GR2HT',
                 organism='Maize', researcher='test_data',
                 sample_name='999999999',
                 develop_stage='v04',
                 growth_location='', treated='0'))
        actual_json = self.client.delete('/sbs/samples/8', data=user_data,
                                         content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    def test_update_visible_to_client(self):
        """
        test case for updating sample visible to client
        """
        user_data = json.dumps(dict(analysis_id_list='1'))
        actual_json = self.client.put('/sbs/analyses/visible', data=user_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

    def test_update_invisible_to_client(self):
        """
        test case for updating sample invisible to client
        """
        user_data = json.dumps(dict(analysis_id_list='1'))
        actual_json = self.client.put('/sbs/analyses/invisible', data=user_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
