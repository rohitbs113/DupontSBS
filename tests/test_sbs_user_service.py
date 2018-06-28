from sqlite_testdb import SqliteTest

from sbs.service import user_service as service


class TestSbsUserAPI(SqliteTest):
    def test_get_latest_load_date(self):
        """
        test cases for adding user
        """
        user_data = dict(username='unittest1', role='lab',
                         active='y')
        output = service.add_user(user_data)
        self.assertEqual(output['status'], 'Success: user-data inserted successfully!')

    def test_set_user_status(self):
        """
        test case for updating user status
        """
        user_data = dict(active='y')
        output = service.set_user_status('unittest', user_data)
        self.assertEqual(output['status'], 'User unittest is activated')

    def test_get_user_by_username(self):
        """
        test cases for getting user
        """
        output = service.get_user_by_username('unittest')
        self.assertEqual(output['user_name'], 'unittest')

    def test_get_current_user_role(self):
        """
        test cases for getting current user role
        """
        output = service.get_current_user_role('unittest')
        self.assertEqual(output, 'lab')
