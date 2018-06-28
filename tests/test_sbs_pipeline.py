from sqlite_testdb import SqliteTest
from unittest.mock import patch

from sbs.service import pipeline_service as service

class TestSbsPipelineServiceAPI(SqliteTest):
    @patch('sbs.service.pipeline_service.submit_job')
    @patch('sbs.service.pipeline_service.get_job_status')
    def test_submit_recalculate_pipeline_call_job_with_success(self,get_job_status,submit_job):
        """
            test cases for checking letest load date
        """
        get_job_status.return_value = 'success'
        submit_job.return_value = {'jobId':'1234'}
        output = service.submit_recalculate_pipeline_call_job('AA171000','1')
        self.assertEqual(output, 'success')

    @patch('sbs.service.pipeline_service.submit_job')
    @patch('sbs.service.pipeline_service.get_job_status')
    def test_submit_recalculate_pipeline_call_job_with_timeout(self, get_job_status, submit_job):
        """
            test cases for checking letest load date
        """
        get_job_status.return_value = 'TIMEOUT'
        submit_job.return_value = {'jobId': '1234'}
        output = service.submit_recalculate_pipeline_call_job('AA171000', '1')
        self.assertEqual(output, 'TIMEOUT')

    @patch('sbs.service.pipeline_service.submit_job')
    @patch('sbs.service.pipeline_service.get_job_status')
    def test_submit_recalculate_pipeline_call_job_with_multiple_samples(self, get_job_status, submit_job):
        """
            test cases for checking letest load date
        """
        get_job_status.return_value = 'TIMEOUT'
        submit_job.return_value = {'jobId': '1234'}
        sample_analysis_list = [{'sample_id':'AA171000','analysis_id':'1'},{'sample_id':'AA171000','analysis_id':'2'},{'sample_id':'AA171000','analysis_id':'3'},{'sample_id':'AA171000','analysis_id':'4'},{'sample_id':'AA171000','analysis_id':'5'}]
        for sample_analysis in sample_analysis_list:
            sample_id = sample_analysis['sample_id']
            analysis_id = sample_analysis['analysis_id']
            output = service.submit_recalculate_pipeline_call_job(sample_id, analysis_id)
            self.assertEqual(output, 'TIMEOUT')
