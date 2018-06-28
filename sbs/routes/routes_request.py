from flask_cors import cross_origin

from sbs.routes.routes import ERROR, REQUIRED_FIELD_REQUEST_ID, SUCCESS, \
    REQUIRED_FIELD_COMMENT
from sbs.service import request_service as req_svc, user_service as user_svc, \
    sample_service as sample_svc
from sbs.service.user_service import authorize
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_SAMPLES = "Samples is a required field."


@app.route('/' + APP_CTX + '/requests', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_request():
    """
    swag_from_file: sbs/swagger/sbs_post_requests.yml
    """
    params = request.get_json(force=True)
    if 'request_id' not in params or not params['request_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)

    try:
        added_request = req_svc.add_request(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, added_request)


@app.route('/' + APP_CTX + '/requests/<request_id>', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def update_request(request_id):
    """
    swag_from_file: sbs/swagger/sbs_put_update_status.yml
    """
    params = request.get_json(force=True)
    params['request_id'] = request_id
    try:
        response = req_svc.update_request(params)
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/requests/<request_id>', methods=['DELETE'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def delete_request(request_id):
    """
    swag_from_file: sbs/swagger/sbs_delete_requests.yml
    """
    try:
        response = req_svc.delete_request(request_id)
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/requests', methods=['GET'])
@cross_origin()
@authorize(['lab', 'client'], require_role=True, require_identity=True)
def get_requests_data():
    """
    swag_from_file: sbs/swagger/sbs_get_requests.yml
    """
    try:
        user_name = get_username()
        role = user_svc.get_current_user_role(user_name)
        result = req_svc.get_requests(role)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/requests/<request_id>/samples',
           methods=['GET'])
@cross_origin()
@authorize(['lab', 'client'], require_role=True, require_identity=True)
def get_samples_data(request_id):
    """
    swag_from_file: sbs/swagger/sbs_get_samples.yml
    """
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)

    try:
        user_name = get_username()
        role = user_svc.get_current_user_role(user_name)
        result = req_svc.get_samples(request_id, role)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/requests/<request_id>/comments',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_request_comment(request_id):
    """
    swag_from_file: sbs/swagger/sbs_get_request_comments.yml
    """
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    try:
        result = req_svc.get_request_comments(request_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/requests/<request_id>/comments',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_request_comment(request_id):
    """
    swag_from_file: sbs/swagger/sbs_post_request_comments.yml
    """
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)

    params = request.get_json(force=True)
    params['username'] = get_username()

    if 'comment' not in params or not params['comment']:
        return create_json_response(ERROR, REQUIRED_FIELD_COMMENT)

    try:
        result = req_svc.add_request_comments(request_id, params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/requests/<request_id>/samples/types/<type>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_sample_by_types(request_id, type):
    """
    swag_from_file: sbs/swagger/sbs_get_individual_sample_by_request_id.yml
    """
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    if not type:
        return create_json_response(ERROR, "Type is required parameter")

    fetch_only_first = request.args.get('first')
    params = {}
    params['request_id'] = request_id
    params['filter_type'] = type
    if fetch_only_first and fetch_only_first == 'true':
        params['fetch_only_first'] = True
    else:
        params['fetch_only_first'] = False

    role = user_svc.get_current_user_role_by_access_token()
    params['role'] = role
    sample = {}
    try:
        results = req_svc.get_sample_by_request_id(params)

        if results:

            request_obj = req_svc.get_request_object(params['request_id'])
            sample = sample_svc.get_sample(results, request_obj)

            if params['fetch_only_first']:
                sample = sample_svc.get_previous_next_sample(sample, request_id, sample['id'],
                                                             sample['analysis_id'], role,
                                                             params['filter_type'])

                constructs = sample['construct_ids']

                junctions = sample_svc.get_junctions(sample['sample_id'],
                                                     params['analysis_id'],
                                                     constructs['primary_map'])

                sample.update(junctions)

    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, sample)


@app.route('/' + APP_CTX + '/requests/<request_id>', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def submit_request(request_id):
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    params = {}
    params['request_id'] = request_id
    samples = request.args.get('samples')

    if not samples:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLES)

    params['samples'] = [x.strip() for x in samples.split(",")]

    try:
        params['type'] = 'delta'
        result = req_svc.submit_request(params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, result)
