from flask_cors import cross_origin

from sbs.routes.routes import ERROR, REQUIRED_FIELD_REQUEST_ID, \
    REQUIRED_FIELD_SAMPLE_ID, SUCCESS, REQUIRED_FIELD_ANALYSIS_ID, logger
from sbs.service import sample_service as sample_svc
from sbs.service import user_service as user_svc
from sbs.service.user_service import authorize
from sbs.utility import *
from sbs.utility import create_json_response

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)


@app.route('/' + APP_CTX + '/samples', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_sample():
    """
    swag_from_file: sbs/swagger/sbs_post_samples.yml
    """
    params = request.get_json(force=True)
    if 'request_id' not in params or not params['request_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    if 'sample_id' not in params or not params['sample_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)

    try:
        response = sample_svc.add_sample(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/samples/<sample_id>', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def update_sample(sample_id):
    """
    swag_from_file: sbs/swagger/sbs_put_samples.yml
    """
    params = request.get_json(force=True)
    params['sample_id'] = sample_id

    try:
        response = sample_svc.update_sample(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/samples/<sample_id>', methods=['DELETE'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def delete_sample(sample_id):
    """
    swag_from_file: sbs/swagger/sbs_delete_samples.yml
    """
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)

    try:
        response = sample_svc.delete_sample(sample_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX +
           '/requests/<request_id>/samples/<sample_id>/analyses/<analysis_id>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_sample_details(request_id, sample_id, analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_individual_sample.yml
    """
    params = {}
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    filter_type = request.args.get('filter_type')
    role = user_svc.get_current_user_role_by_access_token()

    params['request_id'] = request_id
    params['sample_id'] = sample_id
    params['analysis_id'] = analysis_id
    params['filter_type'] = filter_type
    params['role'] = role
    try:
        result = sample_svc.get_sample_details(params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)
