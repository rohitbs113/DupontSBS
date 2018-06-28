from flask_cors import cross_origin
from flask_swagger import swagger

import sbs.database_utility as dbutil
import sbs.service.sample_service as sample_svc
from sbs.service.user_service import authorize
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_REQUEST_ID = "Request id is a required field."
REQUIRED_FIELD_SAMPLE_ID = "Sample id is a required field."
REQUIRED_FIELD_ANALYSIS_ID = "Analysis id is a required field."
REQUIRED_FIELD_COMMENT = "Comment is a required field."
REQUIRED_FIELD_SAMPLE_ID_ANALYSIS_ID_LIST = "Sample_id_Analysis_id_list is " \
                                            "a required field"
ERROR = "Error"
SUCCESS = "Success"


@app.route("/spec")
@cross_origin()
def spec():
    try:
        swag = swagger(app, from_file_keyword='swag_from_file')
        swag['info']['version'] = "1.0.0"
        swag['info']['title'] = "SbS API"

        return jsonify(swag)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)


@app.route('/', methods=['GET'])
def get_api_info():
    try:
        info = {'service_name': 'SBS Api'}
        return create_json_response(SUCCESS, info)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)


@app.route('/' + APP_CTX + '/initdb', methods=['GET'])
def init_db():
    """
    Create MySql tables
    """
    return dbutil.init_mysql_db()


@app.route('/' + APP_CTX + '/reports', methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_report():
    """
    swag_from_file: sbs/swagger/sbs_get_reports.yml
    """
    params = {'sample_id': request.args.get('sample_id'),
              'analysis_id': request.args.get('analysis_id'),
              'integrity': request.args.get('integrity'),
              'junction': request.args.get('junction')}
    if 'sample_id' not in params or not params['sample_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)

    if 'analysis_id' not in params or not params['analysis_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    try:
        result = sample_svc.get_reports(params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/reports', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_multiple_report():
    """
    swag_from_file: sbs/swagger/sbs_post_get_multiple_reports.yml
    """
    params = request.get_json(force=True)
    if 'sample_id_analysis_id_list' not in params or not \
            params['sample_id_analysis_id_list']:
        return create_json_response(ERROR,
                                    REQUIRED_FIELD_SAMPLE_ID_ANALYSIS_ID_LIST)
    try:
        result = sample_svc.get_multiple_reports(params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)
