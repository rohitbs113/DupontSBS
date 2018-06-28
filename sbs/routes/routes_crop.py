from flask_cors import cross_origin

from sbs.routes.routes import ERROR, SUCCESS
from sbs.service import crop_service as crop_svc
from sbs.service.user_service import authorize
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_ORGANISM = "Organism is a required field."


@app.route('/' + APP_CTX + '/crops', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_crop():
    """
    swag_from_file: sbs/swagger/sbs_post_crops.yml
    """
    params = request.get_json(force=True)
    if 'organism' not in params or not params['organism']:
        return create_json_response(ERROR, REQUIRED_FIELD_ORGANISM)

    try:
        crop_result = crop_svc.add_crop(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, crop_result)


@app.route('/' + APP_CTX + '/crops/<crop_id>', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def update_crop(crop_id):
    """
    swag_from_file: sbs/swagger/sbs_put_crop.yml
    """
    params = request.get_json(force=True)
    if 'organism' not in params or not params['organism']:
        return create_json_response(ERROR, REQUIRED_FIELD_ORGANISM)
    params['id'] = crop_id
    try:
        response = crop_svc.update_crop(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/crops/<crop_id>', methods=['DELETE'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def delete_crop(crop_id):
    """
    swag_from_file: sbs/swagger/sbs_delete_crop.yml
    """
    try:
        response = crop_svc.delete_crop(crop_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, response)
