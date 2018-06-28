from flask_cors import cross_origin

import sbs.config as config
import sbs.service.pipeline_configuration_service as configuration_svc
from sbs.routes.routes import ERROR, SUCCESS
from sbs.service.user_service import authorize
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_FILE_NAME = "File Name is a required field."
REQUIRED_FIELD_FILE_CONTENT = "File Content is a required field."


@app.route('/' + APP_CTX + '/pipelines/configs/s3/<config_filename>', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=False, require_identity=True)
def save_pipeline_configuration(config_filename):
    """
    swag_from_file: sbs/swagger/sbs_post_save_configuration_from_s3.yml
    """
    try:
        file_data = configuration_svc.get_config_file_from_s3(config_filename)
        if file_data['file_content']:
            configuration = configuration_svc.save_configuration(file_data['file_name'], file_data['file_content'])
        else:
            raise Exception("No file content on s3 for file {}".format(config_filename))
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, configuration)


@app.route('/' + APP_CTX + '/pipelines/configs/<config_filename>', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=config.REQUIRE_ROLE, require_identity=True)
def save_configuration_new_version(config_filename):
    """
    swag_from_file: sbs/swagger/sbs_post_save_configuration.yml
    """
    params = request.get_json(force=True)
    file_content = params['file_content']
    if not config_filename:
        return create_json_response(ERROR, REQUIRED_FIELD_FILE_NAME)
    if not file_content:
        return create_json_response(ERROR, REQUIRED_FIELD_FILE_CONTENT)

    try:
        configuration = configuration_svc.save_configuration(config_filename, file_content)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, configuration)


@app.route('/' + APP_CTX + '/pipelines/configs', methods=['GET'])
@cross_origin()
@authorize('lab', require_role=config.REQUIRE_ROLE, require_identity=True)
def get_config_files():
    """
    swag_from_file: sbs/swagger/sbs_get_list_conf_files.yml
    """
    try:
        configuration = configuration_svc.list_conf_files()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, configuration)


@app.route('/' + APP_CTX + '/pipelines/configs/<config_filename>', methods=['GET'])
@cross_origin()
@authorize('lab', require_role=config.REQUIRE_ROLE, require_identity=True)
def get_all_config_files_by_name(config_filename):
    """
    swag_from_file: sbs/swagger/sbs_get_all_config_file_versions.yml
    """
    if not config_filename:
        return create_json_response(ERROR, REQUIRED_FIELD_FILE_NAME)
    try:
        configurations = configuration_svc.get_all_versions_by_file_name(config_filename)
        configurations = [config.as_dict() for config in configurations]
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, configurations)
