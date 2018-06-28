from flask_cors import cross_origin

from sbs.models.Analysis import RequestType
from sbs.routes.routes import ERROR, SUCCESS, \
    REQUIRED_FIELD_ANALYSIS_ID, \
    REQUIRED_FIELD_COMMENT, \
    REQUIRED_FIELD_SAMPLE_ID
from sbs.service import analysis_service as analysis_svc
from sbs.service import junction_service as jn_service
from sbs.service import sample_service as sample_svc
from sbs.service import variation_service as variation_svc
from sbs.service.user_service import authorize
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_TYPE = "Type is a required field or " \
                      "Entered value for Type is not matching"
REQUIRED_FIELD_MAP_ID = "Map id is a required field."
REQUIRED_FIELD_CONSTRUCT_ID = "Construct id is a required field."
REQUIRED_FIELD_ANALYSIS_TOOLS_ID = "Analysis Tools id is required"
REQUIRED_FIELD_JUNCTION_ID = "Junction id list is required"
REQUIRED_FIELD_CALL = "Call required"


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/comments',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_analysis_comment(analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_analysis_comments.yml
    """
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    try:
        result = sample_svc.get_analysis_comments(analysis_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/comments',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_analysis_comment(analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_post_analysis_comments.yml
    """
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    params = request.get_json(force=True)
    params['username'] = get_username()

    if 'comment' not in params or not params['comment']:
        return create_json_response(ERROR, REQUIRED_FIELD_COMMENT)

    try:
        result = sample_svc.add_analysis_comments(analysis_id, params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def update_analysis(analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_put_analysis.yml
    """
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    params = request.get_json(force=True)
    params['analysis_id'] = analysis_id

    try:
        response = analysis_svc.update_analysis(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/analyses', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_analysis():
    """
    swag_from_file: sbs/swagger/sbs_post_analysis.yml
    """
    params = request.get_json(force=True)

    if 'sample_id' not in params or not params['sample_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)

    if 'type' not in params \
            or not params['type'] \
            or params['type'].lower() not in RequestType.__members__:
        return create_json_response(ERROR, REQUIRED_FIELD_TYPE)

    try:
        result = analysis_svc.add_analysis(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/integrities',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_integrity(analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_integrity.yml
    """
    map_id = request.args.get('map_id')
    result = []
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    try:
        variations = variation_svc.get_integrities(analysis_id, map_id)
        if variations:
            for variation in variations:
                result.append(variation.as_dict())
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analyses/visible', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def make_visible():
    """
    swag_from_file: sbs/swagger/sbs_put_visible.yml
    """
    params = request.get_json(force=True)
    analysis_id_list = params['analysis_id_list']
    try:
        if analysis_id_list:
            if (sample_svc.batch_update_visible_to_client(analysis_id_list,
                                                          is_visible_to_client=True)):
                return create_json_response(SUCCESS,
                                            "Record updated successfully")
            else:
                return create_json_response(ERROR,
                                            "Error while updating analysis batch visible to client")
        else:
            return create_json_response(ERROR,
                                        "No analysis ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)


@app.route('/' + APP_CTX + '/analyses/invisible', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def make_invisible():
    """
    swag_from_file: sbs/swagger/sbs_put_invisible.yml
    """
    params = request.get_json(force=True)
    analysis_id_list = params['analysis_id_list']
    try:
        if analysis_id_list:
            if (sample_svc.batch_update_visible_to_client(analysis_id_list,
                                                          is_visible_to_client=False)):
                return create_json_response(SUCCESS,
                                            "Record updated successfully")
            else:
                return create_json_response(ERROR,
                                            "Error while updating analysis batch visible to client")
        else:
            return create_json_response(ERROR,
                                        "No analysis ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)


@app.route('/' + APP_CTX + '/junctions/batch', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def junction_batch_insert():
    """
    swag_from_file: sbs/swagger/sbs_post_junction_batch.yml
    """
    params = request.get_json(force=True)
    if 'junctions' not in params or not params['junctions']:
        return create_json_response(ERROR, "junction list is required")
    try:
        junctions_dict_list = params['junctions']
        jn_service.insert_junctions(junctions_dict_list)
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, None)


@app.route('/' + APP_CTX + '/junctions/mask', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def mark_junctions_masked():
    """
    swag_from_file: sbs/swagger/sbs_put_junction_masked.yml
    """
    params = request.get_json(force=True)
    junctions_dict_list = params['junctions']
    junction_comment = params['junction_comment']
    curr_construct_id = params['curr_construct_id']
    curr_sample_id = params['curr_sample_id']
    analysis_id = params['analysis_id']
    try:
        if junctions_dict_list:
            jn_service.update_junction_mask(junctions_dict_list, True,
                                            junction_comment, get_username(),
                                            curr_construct_id,
                                            curr_sample_id, analysis_id)
        else:
            return create_json_response(ERROR,
                                        "No junction ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, "Record updated successfully")


@app.route('/' + APP_CTX + '/junctions/unmask', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def mark_junctions_unmask():
    """
    swag_from_file: sbs/swagger/sbs_put_junction_unmask.yml
    """
    params = request.get_json(force=True)
    junctions_dict_list = params['junctions']
    curr_construct_id = params['curr_construct_id']
    curr_sample_id = params['curr_sample_id']
    analysis_id = params['analysis_id']

    try:
        if junctions_dict_list:
            jn_service.update_junction_mask(junctions_dict_list, False, None,
                                            None, curr_construct_id,
                                            curr_sample_id, analysis_id)
        else:
            return create_json_response(ERROR,
                                        "No junction ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, "Record updated successfully")


@app.route('/' + APP_CTX + '/junctions/mask/duplicates', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def mark_junction_duplicates_masked():
    params = request.get_json(force=True)
    junction_id_list = params['junctions']
    junction_comment = params['junction_comment']
    curr_req_id = params['curr_req_id']
    try:
        if junction_id_list:
            jn_service.update_junction_duplicate_mask(junction_id_list,
                                                      junction_comment,
                                                      curr_req_id, True,
                                                      get_username())
        else:
            return create_json_response(ERROR,
                                        "No junction ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, "Record updated successfully")


@app.route('/' + APP_CTX + '/junctions/unmask/duplicates', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def mark_junction_duplicates_unmasked():
    params = request.get_json(force=True)
    junction_id_list = params['junctions']
    curr_req_id = params['curr_req_id']
    try:
        if junction_id_list:
            jn_service.update_junction_duplicate_mask(junction_id_list, None,
                                                      curr_req_id, False, None)
        else:
            return create_json_response(ERROR,
                                        "No junction ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)
    return create_json_response(SUCCESS, "Record updated successfully")


@app.route('/' + APP_CTX + '/integrities/batch', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def integrity_batch_insert():
    """
    swag_from_file: sbs/swagger/sbs_post_integrity_batch.yml
    """
    params = request.get_json(force=True)
    if 'integrities' not in params or not params['integrities']:
        return create_json_response(ERROR, "integrity list is required")
    try:
        integrity_dict_list = params['integrities']
        analysis_svc.batch_insert_integrities(integrity_dict_list)
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, None)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/analysis_tools',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_call_details(analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_call_details.yml
    """
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    try:
        result = analysis_svc.get_call_details(analysis_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analysis_tools', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_analysis_tools():
    """
    swag_from_file: sbs/swagger/sbs_post_analysis_tools.yml
    """
    params = request.get_json(force=True)
    analysis_tools = params['analysis_tools']
    response = []
    if not analysis_tools:
        return create_json_response(ERROR, "Analysis Tools required")
    try:
        tools_object_list = analysis_svc.add_analysis_tools(analysis_tools)
        if tools_object_list:
            for obj in tools_object_list:
                response.append(obj.as_dict())

    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/analyses/promote_to_alpha', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def promote_to_aplha():
    """
    swag_from_file: sbs/swagger/sbs_put_promote_to_alpha.yml
    """
    params = request.get_json(force=True)
    analysis_id_list = params['analysis_id_list']
    try:
        if analysis_id_list:
            if analysis_svc.batch_update_promote_to_alpha(analysis_id_list):
                return create_json_response(SUCCESS,
                                            "Record updated successfully")
            else:
                return create_json_response(ERROR,
                                            "Error while updating analysis batch promote to alpha")
        else:
            return create_json_response(ERROR,
                                        "No analysis ids found in request")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/maps/<map_id>',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_map_analysis(analysis_id, map_id):
    """
    swag_from_file: sbs/swagger/sbs_post_map_analysis.yml
    """
    params = request.get_json(force=True)

    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_MAP_ID)

    try:
        read_count = params.get('read_count', None)
        result = analysis_svc.add_map_analysis(analysis_id, map_id,
                                               read_count).as_dict()
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/maps', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_map():
    """
    swag_from_file: sbs/swagger/sbs_post_map.yml
    """
    params = request.get_json(force=True)

    if 'construct_id' not in params or not params['construct_id']:
        return create_json_response(ERROR, REQUIRED_FIELD_CONSTRUCT_ID)

    try:
        result = analysis_svc.add_map(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/tools/<tool_id>/details',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_analysis_tool_details(analysis_id, tool_id):
    """
    swag_from_file: sbs/swagger/sbs_post_analysis_tool_details.yml
    """
    params = request.get_json(force=True)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not tool_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_TOOLS_ID)
    if 'call' not in params or not params['call']:
        return create_json_response(ERROR, REQUIRED_FIELD_CALL)

    params['analysis_id'] = analysis_id
    params['tool_id'] = tool_id
    try:
        response = analysis_svc.add_analysis_tool_details(params).as_dict()
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX +
           '/samples/<sample_id>/analyses/<analysis_id>/junctions',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def get_junctions(sample_id, analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_junctions_with_construct.yml
    """
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    construct_id = request.args.get('construct_id')

    if not construct_id:
        return create_json_response(ERROR, REQUIRED_FIELD_CONSTRUCT_ID)

    try:
        result = sample_svc.get_junctions(sample_id, analysis_id, construct_id)
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, result)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/tools/<tool_id>',
           methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def update_analysis_tool_details(analysis_id, tool_id):
    """
    swag_from_file: sbs/swagger/sbs_post_analysis_tool_details.yml
    """
    params = request.get_json(force=True)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not tool_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_TOOLS_ID)

    params['analysis_id'] = analysis_id
    params['tool_id'] = tool_id
    try:
        response = analysis_svc.update_analysis_tool_details(params).as_dict()
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/analyses/<analysis_id>/junctions/endogenous',
           methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_to_endogenous_set(analysis_id):
    """
    """
    params = request.get_json(force=True)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    junction_ids = params['junction_ids']
    if not junction_ids:
        return create_json_response(ERROR, REQUIRED_FIELD_JUNCTION_ID)

    try:
        response = jn_service.set_endogenous_junction(junction_ids)
        if response:
            try:
                jn_service.update_endogenous_set(analysis_id, junction_ids)
            except Exception as e:
                # If endo set updates are failed just log it
                logger.error('An error occurred: {}'.format(str(e)))
        if response:
            return create_json_response(SUCCESS, 'SUCCESS')
        else:
            return create_json_response(ERROR, 'FAILURE')
    except Exception as e:
        logger.error('An error occurred: {}'.format(str(e)))
        return create_json_response(ERROR, e)
