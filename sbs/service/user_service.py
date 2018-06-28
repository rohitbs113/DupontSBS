import logging
from functools import wraps
from six.moves import configparser
import sbs.config as cfg
import os
from sbs.database_utility import db
from sbs.models.UserRole import UserRole
from sbs.utility import *
from sbs.oidc.research_config import config as research_cfg

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def authorize(*roles, require_role=False, require_identity=False):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if require_identity or require_role:
                claims = auth.get_claims(require_identity)
                if not claims:
                    logger.error('Authentication exception. Access denied. {}'.format(str(claims)))
                    return create_json_response('Error', 'Authentication error. Access denied: '
                                                         'You do not have permission to access this url.')
                if require_role:
                    claims = claims['identity']['claims']
                    if (not 'user_name' in claims or not claims['user_name']) and claims['aud'] == research_cfg['research_auth']['client_id']:
                        return f(*args, **kwargs)
                    username = claims['user_name']
                    user_roles = get_current_user_role(username)
                    if user_roles not in roles[0]:
                        logger.error('Authentication error. Access denied.')
                        return create_json_response('Error', 'Authentication error. Access denied: '
                                                             'You do not have permission to access this url.')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def get_user_by_username(user_name):
    """
    Gets SBS user
    """
    try:
        user = UserRole.query.get(user_name)
    except Exception as e:
        raise Exception('Failed to get user with error: ', e)

    return user.as_dict() if user else None


def get_current_user_role(user_name):
    user = get_user_by_username(user_name)
    if user and 'role' in user:
        return user['role']
    else:
        raise Exception("Invalid user for user name {}." \
                        .format(user_name))


def add_user(userdata):
    """
    Adds new user to SBS
    """
    try:
        result = {}
        user_name = userdata['username']
        role = userdata['role']
        if role.lower() == cfg.lab_role or role.lower() == cfg.client_role:
            active = is_active(userdata['active'])
            user_role = UserRole(user_name, role, active)
            db.session.add(user_role)
            db.session.commit()
            result['status'] = 'Success: user-data inserted successfully!'
        else:
            result['status'] = 'Error: Invalid role provided'

    except Exception as e:
        err_type = e.__class__.__name__
        if err_type == 'IntegrityError':
            raise Exception('Failed to add user as it is already authorized with error: ', e)

        raise Exception('Failed to add user with error: ', e)

    return result


def set_user_status(username, userdata):
    """
    Toggles user status between 'y' and 'n'
    """
    try:
        result = {}
        user = UserRole.query.get(username)
        if not user:
            raise Exception("user " + username + " does not exist")
        active_value = is_active(userdata['active'])
        user.active = active_value
        if active_value:
            result['status'] = 'User ' + username + ' is activated'
        else:
            result['status'] = 'User ' + username + ' is deactivated'

        db.session.commit()

    except Exception as e:
        raise Exception('Failed to set user status with error: ', e)

    return result


def is_active(active):
    active_values = ['y', 'yes', 'true']
    if active.lower() in active_values:
        return True
    else:
        return False


def get_current_user_role_by_access_token():
    return get_current_user_role(get_username())
