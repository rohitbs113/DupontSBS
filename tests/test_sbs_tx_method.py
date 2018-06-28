from sqlite_testdb import SqliteTest
from sbs.service import tx_method_service as tx_method_svc


class TestSbsTxMethodApi(SqliteTest):
    def test_add_tx_method(self):
        params = {"tx_method": "Agro"}
        result = tx_method_svc.add_tx_method(params)
        assert result.method_name == "Agro"
