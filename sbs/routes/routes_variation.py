from flask_cors import cross_origin
from sbs.service import variation_service as variation_svc
from sbs.service.user_service import authorize
from sbs.utility import *
from sbs.utility import create_json_response

cors = configure_cors(APP_CTX)
REQUIRED_FIELD_VARIATION_LIST = "Variation list is a required field"

ERROR = "Error"
SUCCESS = "Success"


@app.route('/' + APP_CTX + '/variations', methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def change_tier():
    """
    swag_from_file: sbs/swagger/sbs_put_change_tier.yml
    """
    result = ""
    params = request.get_json(force=True)

    if 'variation_list' not in params or not params['variation_list']:
        create_json_response(ERROR, REQUIRED_FIELD_VARIATION_LIST)

    try:
        result = variation_svc.batch_update_tier(params['variation_list'])
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    if result:

        for variation in result:
            variation['is_tier_label_updated'] = "true" if \
                variation['is_tier_label_updated'] else "false"

    return create_json_response(SUCCESS, result)
