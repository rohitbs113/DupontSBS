from flask_cors import cross_origin

from sbs.routes.routes import ERROR, SUCCESS
from sbs.service import tx_method_service as tx_method_svc
from sbs.service.user_service import authorize
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_TX_METHOD = "Transformation method name is a required field."


@app.route('/' + APP_CTX + '/tx_method', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def add_tx_method():
    """
    swag_from_file: sbs/swagger/sbs_post_tx_method.yml
    """
    params = request.get_json(force=True)
    if 'tx_method' not in params or not params['tx_method']:
        return create_json_response(ERROR, REQUIRED_FIELD_TX_METHOD)

    try:
        tx_method_result = tx_method_svc.add_tx_method(params).as_dict()
    except Exception as e:
        logger.error('An error occurred : '.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, tx_method_result)
