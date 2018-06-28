from flask_cors import cross_origin

import sbs.service.pipeline_service as svc
from sbs.service.user_service import authorize
from sbs.utility import *
import sbs.database_utility as db_util
import sbs.config as cfg

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

cors = configure_cors(APP_CTX)

REQUIRED_FIELD_TYPE = "Invalid request type. Valid values are alpha, alphaD, delta."
SUCCESS = 'Success'
ERROR = 'Error'
REQUIRED_FIELD_REQUEST_ID = "Request id is a required field."
REQUIRED_FIELD_SAMPLE_ID = "Sample id is a required field."
REQUIRED_FIELD_ANALYSIS_ID = "Analysis id is a required field."
REQUIRED_FIELD_JUNCTION_SEQ = "junction seq is a required field."
REQUIRED_FIELD_JUNCTION_END = "junction end is a required field."
REQUIRED_FIELD_MAP_ID = "Map id is a required field."


@app.route('/' + APP_CTX +
           '/pipelines/routine/requests/<request_id>/analyses/<analysis_id>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_routine_pipeline(request_id, analysis_id):
    """
    Run Routine pipeline.
    Request id/project id and type (alpha/delta) are required field.
    Sample id can be provided to the call, if Sample id is not provided then 
    will get all samples for request id and run pipeline for each sample 
    analysis.
    
    :param request_id: project id for samples
    :param analysis_id: analysis id for samples
    :return: job id - latest job id submitted to run
    
    swag_from_file: sbs/swagger/sbs_get_routine_pipeline.yml
    """
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)

    sample_id = request.args.get('sample_id')
    try:
        response = svc.submit_routine_pipeline_job(request_id, sample_id, analysis_id)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Successfully submitted Routine pipeline job [{}]'
                .format(response['jobId']))

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/pipelines/proj_level_dup_detection/'
                           'requests/<request_id>/'
                           'samples/<sample_id>/'
                           'analyses/<analysis_id>/<outfilename>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_proj_level_dup_detection_pipeline(request_id, sample_id,
                                              analysis_id, outfilename):
    """
    swag_from_file: sbs/swagger/sbs_get_dup_detection_pipeline.yml
    """
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    try:
        response = svc.submit_proj_level_dup_detection_pipeline_job(request_id,
                                                                    sample_id,
                                                                    analysis_id,
                                                                    outfilename)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Successfully submitted Project level duplication '
                'detection pipeline job [{}]'
                .format(response['jobId']))

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/pipelines/gene_disruption/'
                           'requests/<request_id>/'
                           'samples/<sample_id>/'
                           'analyses/<analysis_id>/'
                           'maps/<map_id>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_gene_disruption_pipeline(request_id, sample_id, analysis_id, map_id):
    """
    swag_from_file: sbs/swagger/sbs_get_gene_disruption_pipeline.yml
    """
    if not request_id:
        return create_json_response(ERROR, REQUIRED_FIELD_REQUEST_ID)
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_MAP_ID)

    organism = request.args.get('organism')
    nthread = request.args.get('nthread')

    try:
        response = svc.submit_gene_disruption_pipeline_job(request_id,
                                                           sample_id,
                                                           analysis_id,
                                                           map_id,
                                                           organism,
                                                           nthread)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Successfully submitted Gene disruption pipeline job '
                '[{}]'.format(response['jobId']))

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/pipelines/junction_ext/samples/<sample_id>/'
                           'analyses/<analysis_id>/maps/<map_id>', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_junction_ext_pipeline(sample_id, analysis_id, map_id):
    """
    swag_from_file: sbs/swagger/sbs_post_junction_ext_pipeline.yml
    """
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_MAP_ID)

    params = request.get_json(force=True)
    logger.info('Junction_Extension_Params {}'.format(params))
    junction_params_list = params['junction_params']

    if junction_params_list:
        for junction_params in junction_params_list:

            if junction_params:
                junction_seq = junction_params.get('junction_seq', None)
                junction_end = junction_params.get('junction_end', None)

                if not junction_seq:
                    return create_json_response(ERROR, REQUIRED_FIELD_JUNCTION_SEQ)
                if not junction_end:
                    return create_json_response(ERROR, REQUIRED_FIELD_JUNCTION_END)

                try:
                    response = svc.submit_junction_ext_pipeline_job(sample_id,
                                                                    junction_seq,
                                                                    junction_end,
                                                                    analysis_id,
                                                                    map_id)
                except Exception as e:
                    logger.error('An error occurred : {}'.format(str(e)))
                    return create_json_response(ERROR, e)

    logger.info('Successfully submitted Junction Extension pipeline job'
                ' [{}]'.format(response['jobId']))

    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/pipelines/endogenous/samples/<sample_id>/'
                           'analyses/<analysis_id>/maps/<map_id>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_wildtype_pipeline(sample_id, analysis_id, map_id):
    """
    swag_from_file: sbs/swagger/sbs_get_wildtype_pipeline.yml
    """
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not map_id:
        return create_json_response(ERROR, REQUIRED_FIELD_MAP_ID)
    try:
        response = svc.submit_wildtype_pipeline_job(sample_id,
                                                    analysis_id,
                                                    map_id)

    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Successfully submitted endogenous pipeline job [{}]'
                .format(response['jobId']))
    return create_json_response(SUCCESS, response)


@app.route('/' + APP_CTX + '/pipelines/recalculate_call/samples/<sample_id>/'
                           'analyses/<analysis_id>', methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_recalculate_call(sample_id, analysis_id):
    """
    swag_from_file: sbs/swagger/sbs_get_recalculate_call_pipeline.yml
    """
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    try:
        waiting_time = False
        status = svc.submit_recalculate_pipeline_call_job(sample_id, analysis_id, waiting_time)

    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Recalculate call pipeline job status [{}]'.format(status))
    return create_json_response(SUCCESS, {'job_status': status})


@app.route('/' + APP_CTX + '/pipelines/recalculate_call/samples', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_multiple_recalculate_call():
    params = request.get_json(force=True)
    sample_analysis_list = params['sample_analysis_list']
    waiting_time = False
    status_list = []
    if sample_analysis_list:
        for sample_analysis in sample_analysis_list:
            if sample_analysis:
                sample_id = sample_analysis['sample_id']
                analysis_id = sample_analysis['analysis_id']
                if not sample_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
                if not analysis_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
                try:
                    status = svc.submit_recalculate_pipeline_call_job(sample_id, analysis_id, waiting_time)
                    status_list.append(status)
                    logger.info('Recalculate call pipeline job status [{}]'.format(status))
                except Exception as e:
                    logger.error('An error occurred : {}'.format(str(e)))
                    return create_json_response(ERROR, e)
        return create_json_response(SUCCESS, status_list)


@app.route('/' + APP_CTX + '/pipelines/regenerate_observed_map/samples/<sample_id>/'
                           'analyses/<analysis_id>/observed_maps/<new_map_id>',
           methods=['GET'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_regenerate_observed_map_call(sample_id, analysis_id, new_map_id):
    """
    swag_from_file: sbs/swagger/sbs_get_regenerate_observed_map_call_pipeline.yml
    """
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not new_map_id:
        return create_json_response(ERROR, "new_map_id is required field")

    slices = request.args.get("slices")

    params = dict(sample_id=sample_id, analysis_id=analysis_id,
                  new_map_id=new_map_id, analysis_read_dir=cfg.analysis_read_dir_expected,
                  slices=slices)
    try:
        status = svc.submit_regenerate_observed_map_call_job(params)

    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Regenerate observed map call pipeline job status [{}]'.format(status))
    return create_json_response(SUCCESS, {'job_status': status})


@app.route('/' + APP_CTX + '/pipelines/regenerate_observed_map/samples/<sample_id>/'
                           'analyses/<analysis_id>/observed_maps/<new_map_id>',
           methods=['PUT'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_regenerate_observed_map_update_call(sample_id, analysis_id, new_map_id):
    if not sample_id:
        return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
    if not analysis_id:
        return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
    if not new_map_id:
        return create_json_response(ERROR, "new_map_id is required field")

    slices = request.args.get("slices")
    
    # Gets latest observed map variation DB records and upload to s3
    db_util.upload_latest_db_records('variation', sample_id, analysis_id, new_map_id)

    params = dict(sample_id=sample_id, analysis_id=analysis_id,
                  new_map_id=new_map_id, analysis_read_dir= cfg.analysis_read_dir_observed,
                  slices=slices)
    try:
        status = svc.submit_regenerate_observed_map_call_job(params)

    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        return create_json_response(ERROR, e)

    logger.info('Update observed map update pipeline job status [{}]'.format(status))
    return create_json_response(SUCCESS, {'job_status': status})


@app.route('/' + APP_CTX + '/pipelines/regenerate_observed_map/samples', methods=['POST'])
@cross_origin()
@authorize('lab', require_role=True, require_identity=True)
def execute_multiple_regenerate_observed_map_call():
    params = request.get_json(force=True)
    sample_analysis_map_list = params['request_maps']
    status_list = []
    if sample_analysis_map_list:
        for sample_analysis_map in sample_analysis_map_list:
            if sample_analysis_map:
                sample_id = sample_analysis_map['sample_id']
                analysis_id = sample_analysis_map['analysis_id']
                new_map_id = sample_analysis_map['new_map_id']
                if not sample_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_SAMPLE_ID)
                if not analysis_id:
                    return create_json_response(ERROR, REQUIRED_FIELD_ANALYSIS_ID)
                if not new_map_id:
                    return create_json_response(ERROR, "new_map_id is required field")
                batch_params = {}
                batch_params['sample_id'] = sample_id
                batch_params['analysis_id'] = analysis_id
                batch_params['new_map_id'] = new_map_id
                batch_params['analysis_read_dir'] = cfg.analysis_read_dir_expected
                try:
                    status = svc.submit_regenerate_observed_map_call_job(batch_params)
                    status_list.append(status)
                    logger.info('Regenerate observed map call pipeline job status [{}]'.format(status))
                except Exception as e:
                    logger.error('An error occurred : {}'.format(str(e)))
                    return create_json_response(ERROR, e)

    return create_json_response(SUCCESS, status_list)
