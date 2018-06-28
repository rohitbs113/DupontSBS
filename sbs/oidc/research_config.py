import six
import os
from six.moves import configparser
from research_auth.flask_ext import FlaskOpenIdClient
from sbs import app
import flask

auth = FlaskOpenIdClient()
config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
config_ini_path = os.path.join(dir_path, 'config.ini')
config.read(config_ini_path)
app.config.from_mapping(config['flask'])
# config can be any sort of mapping type
auth.init(config['research_auth'])

