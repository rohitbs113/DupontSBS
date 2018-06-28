from sqlite_testdb import SqliteTest

from sbs.service import request_service as service


class TestSbsRequestAPI(SqliteTest):
    def test_get_latest_load_date(self):
        """
            test cases for checking letest load date
        """
        output = service.get_latest_load_date(['2017-09-20 00:00:00'])
        self.assertEqual(output, '2017-09-20 00:00:00')

    def test_get_latest_multiple_load_date(self):
        """
            test cases for checking letest load date with multiple dates
        """
        output = service.get_latest_load_date(['2017-06-20 00:00:00',
                                               '2015-08-10 00:00:00'])
        self.assertEqual(output, '2017-06-20 00:00:00')

    def test_get_latest_no_load_date(self):
        """
            test cases for checking letest load date with no date
        """
        output = service.get_latest_load_date('')
        self.assertEqual(output, '')

    def test_get_alpha_delta_count(self):
        """
        Tests if method returns expected count for aplha and delta values
        """
        alpha_count, delta_count = service.get_alpha_delta_count(
            '2;1;alpha,2;2;alpha,2;3;delta'.split(','))
        self.assertEqual(alpha_count, 1)
        self.assertEqual(delta_count, 1)

    def test_get_alpha_delta_count_with_missing_type_value(self):
        """
        Tests if method returns expected count for aplha and delta values
        """
        alpha_count, delta_count = service.get_alpha_delta_count(
            '2;1;alpha,2;2;alpha,2;3;delta,1;2'.split(','))
        self.assertEqual(alpha_count, 1)
        self.assertEqual(delta_count, 1)

    def test_get_variation_count(self):
        """
        Test if method returns expected variation count
        """
        tier_label_list = ['Ignore', 'update_map', 'Ignore', 'update_map',
                           'Ignore']
        count = service.get_variation_count(tier_label_list)
        self.assertEqual(count, 2)
