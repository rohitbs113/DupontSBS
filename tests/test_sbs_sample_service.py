from sqlite_testdb import SqliteTest

from sbs.service import sample_service as service


class TestSbsSampleAPI(SqliteTest):
    def test_add_sample(self):
        """
        test cases for adding user
        """
        user_data = dict(primary_map='test_data', ev_man_event='test_data',
                 other_maps='test_data',
                 request_id='1', construct_name='test_data',
                 event_id='zm047.032.2.1.2',
                 geno_type='GR2HT',
                 organism='Maize', researcher='test_data',
                 sample_name='999999999',
                 develop_stage='v04',
                 growth_location='', sample_id='AA0171009',
                 curr_alpha_analysis='1')
        output = service.add_sample(user_data)
        self.assertEqual(output.request_id, 1)

    def test_update_sample(self):
        """
        test cases for update sample
        """
        user_data = dict(primary_map='test_data', ev_man_event='test_data',
             other_maps='test_data',
             request_id='AA200', construct_name='test_data',
             event_id='zm047.032.2.1.2',
             geno_type='GR2HT',
             organism='Maize', researcher='test_data',
             sample_name='123456789',
             develop_stage='v04',
             growth_location='', sample_id='AA0171001')
        output = service.update_sample(user_data)
        self.assertEqual(output.sample_name, '123456789')

    def test_delete_sample(self):
        """
        test cases for delete sample
        """
        output = service.delete_sample(1)
        self.assertEqual(output['status'], 'Deleted sample for id [1]')

    def test_batch_update_visible_to_client(self):
        """
        test cases for batch_update_visible_to_client
        """
        output = service.batch_update_visible_to_client('1',True)
        self.assertEqual(output,True)
