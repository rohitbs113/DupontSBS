from flask_cors import cross_origin


from sbs.routes.routes import ERROR, SUCCESS
from sbs.service import jbrowse_service as jbrowse_svc
from sbs.service import msa_service as msa
from sbs.utility import *

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_PATH = "Path is a required field"
REQUIRED_FIELD_MAP_TYPE = "Map Type is a required field"


@app.route('/' + APP_CTX + '/jbrowse/tracklisturls', methods=['GET'])
@cross_origin()
def get_tracklist_urls():
    path = request.args.get('path')
    map_type = request.args.get('map')
    track_type = request.args.get('track_type')
    if not path:
        return create_json_response(ERROR, REQUIRED_FIELD_PATH)
    if not map_type:
        return create_json_response(ERROR, REQUIRED_FIELD_MAP_TYPE)
    try:
        tracklist_response = jbrowse_svc.get_tracklist_urls(path, map_type, track_type)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, tracklist_response)


@app.route('/' + APP_CTX + '/jbrowse/file', methods=['GET'])
@cross_origin()
def get_jbrowse_file_data():
    path = request.args.get('path')
    if not path:
        return create_json_response(ERROR, REQUIRED_FIELD_PATH)

    try:
        file_response = jsonify(jbrowse_svc.get_dynamic_response(path))
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return file_response


@app.route('/' + APP_CTX + '/jbrowse/msa', defaults={'path': ''}, methods=['GET'])
@app.route('/' + APP_CTX + '/jbrowse/msa/<path:path>', methods=['GET'])
@cross_origin()
def get_msa_view_data(path):
    start = request.args.get('start')
    end = request.args.get('end')
    bamfile_type = request.args.get('type')
    if not path:
        return create_json_response(ERROR, REQUIRED_FIELD_PATH)
    if not start:
        return create_json_response(ERROR, 'Start is a required field')
    if not end:
        return create_json_response(ERROR, 'End is a required field')
    if not bamfile_type:
        return create_json_response(ERROR, 'Bam file type is a required field')
    try:
        msa_response = msa.get_msa_view_data(path, start, end, bamfile_type) 
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, msa_response)
