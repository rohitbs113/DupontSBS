import json

from sqlite_testdb import SqliteTest


class TestSbsIntegrityApi(SqliteTest):
    def test_add_sample_rest(self):
        """
        test case for batch inserting Integrities
        """
        integrity_data = [
                {
                    "map_analysis_id": "23",
                    "position": "16904",
                    "purity": "0.98",
                    "read_depth": "269",
                    "ref_base": "T",
                    "tier": "T",
                    "tier_label": "T",
                    "type": "SNP"
                }
        ]
        

        actual_json = self.client.post('/sbs/analyses/123/maps/12345/integrities/batch',
                                       data=json.dumps(integrity_data), content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])

