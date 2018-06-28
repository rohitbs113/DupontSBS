import json
from sbs.service import pipeline_configuration_service as service
from sqlite_testdb import SqliteTest


class TestSbsPipelineConfigurationApi(SqliteTest):
    def test_save_configuration_new_version(self):
        """
        test case for saving sbs pipeline configuration
        """
        config = service.save_configuration('test.txt', "file_content")
        self.assertEqual('test.txt', config.name)

    def test_get_config_files(self):
        """
        test case for listing sbs pipeline configuration files
        """
        config_file_name_list = service.list_conf_files()
        file_name = config_file_name_list[0].name
        self.assertEqual('test.txt', file_name)

    def test_get_all_config_files_by_name(self):
        """
        test case for listing sbs pipeline configuration file's all versions
        """
        config_list = service.get_all_versions_by_file_name("test.txt")
        self.assertEqual(1, config_list[0].version)
