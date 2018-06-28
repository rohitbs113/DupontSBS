from flask_cors import cross_origin

from sbs.routes.routes import ERROR, \
    SUCCESS, logger, \
    REQUIRED_FIELD_COMMENT
from sbs.service import observed_map_service as observed_map_svc
from sbs.service.user_service import authorize
from sbs.utility import *
from sbs.utility import create_json_response

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_CONSTRUCT_ID = "Construct id is a required field."
REQUIRED_FIELD_SAMPLE_ID = "Sample id is a required field."
REQUIRED_FIELD_ANALYSIS_ID = "Analysis id is a required field."
REQUIRED_FIELD_MAP_ID = "Map id is a required field."
REQUIRED_FIELD_OBSERVED_MAP_ID = "ObservedMap id is a required field."


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/observed_maps',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_observed_maps(analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_observed_maps.yml
    """
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    try:
        result = observed_map_svc.get_observed_maps(analysis_id)
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/samples/<sample_id>/analyses/<analysis_id>'
                           '/maps/<map_id>/observed_maps',
            methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_observed_map(sample_id, analysis_id, map_id):
    """
    swag_from_file: sbs/swagger/sbs_post_observed_map.yml
    """
    params = request.get_json(force=True)

    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_MAP_ID)

    params['sample_id'] = sample_id
    params['analysis_id'] = analysis_id
    params['map_id'] = map_id
    try:
        result = observed_map_svc.add_observed_map(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/samples/observed_maps',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_observed_maps():
    """
    swag_from_file: sbs/swagger/sbs_post_observed_map_multiple.yml
    """
    params = request.get_json(force=True)

    request_maps = params['request_maps']
    status_list = []
    if request_maps:
        for request_map_dict in request_maps:
            if request_map_dict:
                sample_id = request_map_dict['sample_id']
                analysis_id = request_map_dict['analysis_id']
                map_id = request_map_dict['map_id']
                if not sample_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
                if not analysis_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
                if not map_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_MAP_ID)
                obs_params = {}
                obs_params['sample_id'] = sample_id
                obs_params['analysis_id'] = analysis_id
                obs_params['map_id'] = map_id
                try:
                    status = observed_map_svc.add_observed_map(obs_params).as_dict()
                    status_list.append(status)
                except Exception as e:
                    logger.error('An error occurred : {}'.format(str(e)))
                    return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, status_list)


@app.route('/' + APP_CTX + '/observed_maps/<observed_map_id>',
           methods=['DELETE'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def delete_observed_map(observed_map_id):
    """
    swag_from_file: sbs/swagger/sbs_delete_observed_map.yml
    """

    if not observed_map_id:
        return create_json_response(ERROR,
                                    "Observed Map Id is a required filed")

    try:
        observed_map_svc.delete_observed_map(observed_map_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, None)


@app.route('/' + APP_CTX + '/observed_maps/<observed_map_id>/comments',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_observed_map_comment(observed_map_id):
    """
    swag_from_file: sbs/swagger/sbs_get_observed_map_comments.yml
    """
    if not observed_map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_OBSERVED_MAP_ID)

    try:
        result = observed_map_svc.get_observed_map_comment(observed_map_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    result_list = []

    for observed_map_comment in result:
        result_list.append(observed_map_comment.as_dict())

    return create_json_response(SUCCESS, result_list)


@app.route('/' + APP_CTX + '/observed_maps/<observed_map_id>/comments',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_observed_map_comment(observed_map_id):
    """
    swag_from_file: sbs/swagger/sbs_post_observed_map_comments.yml
    """
    if not observed_map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_OBSERVED_MAP_ID)

    params = request.get_json(force=True)
    params['username'] = get_username()

    if 'comment' not in params or not params['comment']:
        return create_json_response(ERROR, REQUIRED_FIELD_COMMENT)

    try:
        result = observed_map_svc.add_observed_map_comments(observed_map_id,
                                                            params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)
