from flask_cors import cross_origin


from sbs.routes.routes import SUCCESS, ERROR
from sbs.service import user_service as user_svc
from sbs.utility import *
from sbs.service.user_service import authorize

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)


@app.route('/' + APP_CTX + '/users', methods=['POST'])
@cross_origin()
def add_new_user():
    """
    swag_from_file: sbs/swagger/sbs_post_users.yml
    """
    try:
        user_params = request.get_json(force=True)
        return create_json_response(SUCCESS,
                                    user_svc.add_user(user_params))
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)


@app.route('/' + APP_CTX + '/users/<username>', methods=['PUT'])
@cross_origin()
def update_user_status(username):
    """
    swag_from_file: sbs/swagger/sbs_put_users.yml
    """
    user_params = request.get_json(force=True)

    try:
        user_response = user_svc.set_user_status(username, user_params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, user_response)


@app.route('/' + APP_CTX + '/users', methods=['GET'])
@cross_origin()
@authorize('lab', require_role=False, require_identity=True)
def get_user():
    """
    swag_from_file: sbs/swagger/sbs_get_users.yml
    """
    user_name = get_username()
    logger.info('Get role for username {}'.format(user_name))

    try:
        user = user_svc.get_user_by_username(user_name)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    if user:
        return create_json_response(SUCCESS, user)
    else:
        return create_json_response(ERROR, "Invalid user")
