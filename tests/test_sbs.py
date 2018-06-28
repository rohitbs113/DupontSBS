import json

import pytest
from flask_testing import TestCase
from flask import Flask

from sbs import app
#from sbs.routes import routes


@pytest.fixture
def app_client(request):
    client = app.test_client()
    return client


def test_sbs_index_page(app_client):
    actual_response = app_client.get('/')
    actual_response = json.loads(actual_response.get_data(as_text=True))
    assert actual_response['data']['service_name'] == 'SBS Api'
