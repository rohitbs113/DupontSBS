import json
from datetime import datetime

from sqlite_testdb import SqliteTest


class TestSbsUserApi(SqliteTest):
    def test_add_analysis_rest(self):
        time_dict = {'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
        temp_dict = dict(input_map="test_data", sample_id="AA0171000",
                         reference="test_data",
                         job_status="Complete", sbs_status="Awaiting QC",
                         sbs_version="Sbs_Maize_Agro_v2",
                         pipeline_call="Tier 1", current_call="Tier 1",
                         geno_type="GR2HT",
                         event_id="zm047.032.2.1.2", backbone_call="test_data",
                         sample_call="test_data", sbs_integ_tier="test_data",
                         vqc_ali_pct="test_data",
                         single_read_count="242", paired_read_count="242",
                         complete_probe_coverage="No", target_rate="8.11",
                         tier_3_reason="Incomplete Coverage")
        temp_dict.update(time_dict)
        user_data = json.dumps(temp_dict)
        actual_json = self.client.post('/sbs/analyses', data=user_data,
                                       content_type='application/json')
        actual_json = json.loads(actual_json.data)
        #self.assertEqual('Success', actual_json['status']['message'])

    def test_update_promote_to_aplha(self):
        """
        test case for updating promote to aplha
        """
        user_data = json.dumps(dict(analysis_id_list='1'))
        actual_json = self.client.put('/sbs/analyses/promote_to_alpha', data=user_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Error', actual_json['status']['message'])

    def test_update_promote_to_aplha_success(self):
        """
        test case for updating promote to aplha
        """
        user_data = json.dumps(dict(analysis_id_list='2'))
        actual_json = self.client.put('/sbs/analyses/promote_to_alpha', data=user_data,
                                      content_type='application/json')
        actual_json = json.loads(actual_json.data)

    def test_get_call_details(self):
        """
        Tests if expected details are correct or not
        """
        actual_json = self.client.get('/sbs/analyses/1/calls/pipeline')
        actual_json = json.loads(actual_json.data)
        self.assertEqual('Success', actual_json['status']['message'])
        self.assertEqual('SbS_Maize_SSI', actual_json['data']['prep_method'])

