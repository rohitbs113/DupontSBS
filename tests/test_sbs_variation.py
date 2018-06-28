import json

from sqlite_testdb import SqliteTest


class TestSbsVariationApi(SqliteTest):
    def test_get_integrity(self):
        """
        Tests if expected result is returned for integrity api
        """
        actual_json = self.client.get('/sbs/analyses/1/integrities')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual(1, actual_json['data'][0]['id'])

    def test_update_tier(self):
        """
        Tests if tier_label is updated for single or multiple variation
        """
        variation_list = [dict(variation_id=1, tier_label='Ignore')]
        request_data = json.dumps(dict(variation_list=variation_list))
        actual_json = self.client.put('/sbs/variations', data=request_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual(1, actual_json['data'][0]['id'])

    def test_update_tier_with_incorrect_variation_id(self):
        """
        Tests if error is returned for incorrect variation_id
        """
        variation_list = [dict(variation_id='2a', tier_label='Ignore')]
        request_data = json.dumps(dict(variation_list=variation_list))
        actual_json = self.client.put('/sbs/variations', data=request_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Error', actual_json['status']['message'])
