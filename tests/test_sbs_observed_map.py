from datetime import datetime

from sqlite_testdb import SqliteTest

from sbs.models.ObservedMap import ObservedMap
from sbs.service import observed_map_service as observed_map_svc


class TestSbsObservedMapApi(SqliteTest):
    def test_add_observed_map(self):
        load_time = datetime(2018, 2, 26, 10, 10, 10)
        observed_map = {
            "construct_id": "PHX367.1.1",
            "status": "Ignored",
            "load_time": load_time,
            "sample_id": "1",
            "analysis_id": "1",
            "map_id": "PHX367"
        }
        result = observed_map_svc.add_observed_map(observed_map)

        assert result.status == "Ignored"

    def test_delete_observed_map(self):
        observed_map_svc.delete_observed_map(501)
        result = ObservedMap.query.filter_by(id=501).one_or_none()
        assert result is None

    def test_add_pending_observed_map(self):
        load_time = datetime(2018, 2, 26, 10, 10, 10)
        observed_map = {
            "load_time": load_time,
            "sample_id": "1",
            "analysis_id": "1",
            "map_id": "PHX367"
        }
        result = observed_map_svc.add_observed_map(observed_map)

        assert result.status == "pending"
        assert result.construct_id == 'PHX367.1.1'

    def test_add_latest_version_of_observed_map(self):
        load_time = datetime(2018, 2, 26, 10, 10, 10)
        observed_map = {
            "load_time": load_time,
            "sample_id": "1",
            "analysis_id": "1",
            "map_id": "PHX367"
        }
        observed_map_svc.add_observed_map(observed_map)
        observed_map_svc.add_observed_map(observed_map)
        result = observed_map_svc.add_observed_map(observed_map)
        assert result.construct_id == 'PHX367.1.3'

    def test_get_observed_map(self):
        load_time = datetime(2018, 2, 26, 10, 10, 10)
        observed_map = {
            "construct_id": "PHX367.1.0",
            "status": "Ignored",
            "load_time": load_time,
            "sample_id": "1",
            "analysis_id": "1",
            "map_id": "PHX367"
        }
        observed_map_2 = {
            "construct_id": "PHX368.1.0",
            "status": "Ignored",
            "load_time": load_time,
            "sample_id": "1",
            "analysis_id": "1",
            "map_id": "PHX367"
        }
        observed_map_pending = {
            "load_time": load_time,
            "sample_id": "1",
            "analysis_id": "1",
            "map_id": "PHX367"
        }

        # Add 2 observed maps with Ignored status
        observed_map_svc.add_observed_map(observed_map)
        observed_map_svc.add_observed_map(observed_map_2)

        # Add 2 observed maps with pending status
        observed_map_svc.add_observed_map(observed_map_pending)
        observed_map_svc.add_observed_map(observed_map_pending)

        observed_maps = observed_map_svc.get_observed_maps(1)

        # test should get only 2 observed maps which are in ignored status
        assert len(observed_maps) == 2
