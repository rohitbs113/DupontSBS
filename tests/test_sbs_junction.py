import json
from sbs.service import junction_service as service
from sqlite_testdb import SqliteTest


class TestSbsJunctionApi(SqliteTest):
    def test_add_junction(self):
        """
        test case for batch inserting Junctions
        """
        junction_data = [
            {
                'end': '5p', 'proximal_mapping': 'V008644,3941,3960,100',
                'endogenous': 1,
                'distal_mapping': 'ZmChr10v2,152595281,152596216,91.03',
                'junction_seq': 'CAAACT',
                'proximal_seq': 'TCAGG',
                'proximal_len': '917', 'distal_seq': 'TCAGTGATGACGACGGTG',
                'distal_len': '892', 'element': '"ZM-WUS2_(ALT1)":3569-4477', 'junction_pos': '3941',
                'uniq_reads': '70', 'supporting_reads': '965', 'endogenous': 'True', 'masked': 'False',
                'map_analysis_id': 888, 'junction_sequence': '', 'proximal_sequence': '', 'distal_sequence_length': '',
                'position': '', 'unique_reads': ''
            }
        ]
        self.assertEqual(True, service.insert_junctions(junction_data))

    def test_update_junction_mask(self):
        """
        test case for batch updating Junctions
        """
        self.assertEqual(True, service.update_junction_mask([{'id': 1, 'position': 6789}], True, 'junction_comment',
                                                            'system', 'PHX5902', 'SA171001', 888))
