import logging
import os
import boto3
import sbs.config as config
import base64

from sbs.oidc.research_config import auth
from flask import request
from six.moves import configparser
from sbs.config import log_level
from sbs import app
from flask import jsonify
from flask_cors import CORS

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
APP_CTX = "sbs"


def set_log_level():
    __log_level = str(config.log_level).upper()
    if __log_level == 'INFO':
        ll = logging.INFO
    elif __log_level == 'DEBUG':
        ll = logging.DEBUG
    elif __log_level == 'WARNING':
        ll = logging.WARNING
    elif __log_level == 'ERROR':
        ll = logging.ERROR
    elif __log_level == 'CRITICAL':
        ll = logging.CRITICAL
    elif __log_level == 'NOTSET':
        ll = logging.NOTSET
    else:
        raise Exception('Invalid log level: {}'.format(__log_level))

    return ll


log_level = set_log_level()


def configure_cors(api_route):
    """
    This method set CORS configuration for passed api route
    """

    cors = CORS(app,
                resources={r"/" + api_route + "/*":
                    {"origins": [
                        "*.phibred.com",
                        "*.phitr.com",
                        "*.phiqa.com",
                        "*.phidev.com",
                        ".phisb.com",
                        "localhost",
                        "localhost:"
                    ]
                    }
                }
                )
    return cors


def create_json_response(message, data):
    if isinstance(data, Exception):
        data = ' : '.join([str(data.__class__.__name__), str(data)])
    json_response = jsonify(
        {'api_version': config.version, 'status': {'message': message},
         'data': data})
    return json_response


def create_s3_folder(key):
    try:
        client = boto3.client('s3', region_name=config.aws_region)
        bucket = config.s3_bucket
        client.put_object(
            Bucket=bucket,
            Body='',
            Key=key + "/"
        )
        return os.path.join(bucket, key)
    except Exception as e:
        raise Exception('Failed to create S3 key with error: {}'
                        .format(key, str(e)))


def pad_base64(base_64data):
    while len(base_64data) % 4 != 0:
        base_64data += "="
    return base_64data


def get_username():
    id_token = get_id_token()
    token_parts = id_token.split(".")
    claims_base64 = pad_base64(token_parts[1])
    claims_bytes = base64.b64decode(claims_base64)
    claims_str = claims_bytes.decode('utf-8')
    claims = eval(claims_str)

    if (not 'user_name' in claims or not claims['user_name']) and claims['aud'] == config['client_id']:
        return None

    user_name = claims['user_name']
    logger.info("User name is: {}".format(user_name))
    return user_name


def get_access_token():
    token = None
    id_header = 'X-Res-Identity'
    if id_header in request.headers and request.headers[id_header]:
        token = request.headers[id_header]
    else:
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            token = request.headers['Authorization'].split(maxsplit=1)[1].strip()
        if 'access_token' in request.form:
            token = request.form['access_token']
        elif 'access_token' in request.args:
            token = request.args['access_token']

    return token


def get_id_token():
    token = None
    id_header = 'X-Research-Identity'
    if id_header in request.headers and request.headers[id_header]:
        token = request.headers[id_header]

    return token
