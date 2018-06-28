import logging
import os
import re

import boto3

import sbs.config as cfg
import sbs.database_utility as db_util
import sbs.service.jbrowse_service as jbrowse_svc
import sbs.service.request_service as req_svc
from sbs.models.Analysis import Analysis
from sbs.models.Analysis import RequestType
from sbs.models.AnalysisComment import AnalysisComment
from sbs.models.Crop import Crop
from sbs.models.Junction import Junction
from sbs.models.Map import Map
from sbs.models.MapAnalysis import MapAnalysis
from sbs.models.MapAnalysisJunctions import MapAnalysisJunctions
from sbs.models.Request import Request
from sbs.models.Sample import Sample
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def add_sample(params):
    """
    Adds sample record or raise exception if already exists
    """
    try:
        request_id = params['request_id']
        request = Request.query.filter_by(id=request_id).one_or_none()

        if not request:
            logger.error("Request with id [{}] does not exist."
                         .format(params['request_id']))

        sample_id = params['sample_id']
        sample = Sample.query.filter_by(sample_id=sample_id).one_or_none()

        if sample:
            logger.info("Sample with sample_id [{}] already exists."
                        .format(params['sample_id']))
            return sample

        primary_map = params.get('primary_map', None)
        ev_man_event = params.get('ev_man_event', None)
        other_maps = params.get('other_maps', None)
        construct_name = params.get('construct_name', None)
        event_id = params.get('event_id', None)
        geno_type = params.get('geno_type', None)
        organism = params.get('organism', None)
        sample_name = params.get('sample_name', None)
        develop_stage = params.get('develop_stage', None)
        growth_location = params.get('growth_location', None)
        treated = params.get('treated', False)
        eu_id = params.get('eu_id', None)
        curr_alpha_analysis = params.get('curr_alpha_analysis', None)

        if curr_alpha_analysis:
            update_analysis_type(curr_alpha_analysis)

        sample = Sample(sample_id,
                        primary_map,
                        ev_man_event,
                        other_maps,
                        request_id,
                        construct_name,
                        event_id,
                        geno_type,
                        organism,
                        sample_name,
                        develop_stage,
                        growth_location,
                        treated,
                        eu_id,
                        curr_alpha_analysis)
        db_util.db_add_query(sample)
        db_util.db_commit()
        logger.info("Sample record for request id [{}] added successfully."
                    .format(params['request_id']))

        sample = Sample.query.filter_by(sample_id=sample_id).one_or_none()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to add Sample with error: ', e)

    return sample


def update_sample(params):
    """
    Update sample record
    """
    try:
        sample = Sample.query.filter_by(sample_id=params.get('sample_id')).one()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to get Sample with error: ', e)

    # get rquest primary id
    request_primary_id = None
    request_id = params.get('request_id', None)
    request_object = req_svc.get_request_object(request_id)

    if request_object:
        request_primary_id = request_object.id

    if not request_primary_id:
        raise Exception(
            'Failed to get request primary id for Request: {}'.format(
                request_id))

    sample.primary_map = params.get('primary_map', sample.primary_map)
    sample.ev_man_event = params.get('ev_man_event', sample.ev_man_event)
    sample.other_maps = params.get('other_maps', sample.other_maps)
    sample.construct_name = params.get('construct_name', sample.construct_name)
    sample.event_id = params.get('event_id', sample.event_id)
    sample.geno_type = params.get('geno_type', sample.geno_type)
    sample.organism = params.get('organism', sample.organism)
    sample.sample_name = params.get('sample_name', sample.sample_name)
    sample.develop_stage = params.get('develop_stage', sample.develop_stage)
    sample.growth_location = params.get('growth_location',
                                        sample.growth_location)
    sample.treated = params.get('treated', sample.treated)
    sample.eu_id = params.get('eu_id', sample.eu_id)
    sample.request_id = params.get(request_primary_id, sample.request_id)

    if 'curr_alpha_analysis' in params and params['curr_alpha_analysis']:
        update_analysis_type(params['curr_alpha_analysis'])

    sample.curr_alpha_analysis = params.get('curr_alpha_analysis',
                                            sample.curr_alpha_analysis)

    try:
        db_util.db_commit()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to commit with error: ', e)

    logger.info("Successfully updated sample for id [{}]."
                .format(params['sample_id']))

    return sample


def update_analysis_type(curr_alpha_analysis):
    """
    Updates Analysis type to AlphaD if updated curr_alpha_analysis
    refers to Analysis with type Delta
    """
    try:
        result = Analysis.query.get(curr_alpha_analysis)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update Analysis with error: ', e)

    if result:
        type = result.type

    if type == RequestType.delta:
        result.type = RequestType.alphad


def delete_sample(id):
    """
    delete sample
    """
    try:
        sample = Sample.query \
            .filter_by(id=id) \
            .delete()
        db_util.db_commit()

        if sample:
            return {"status": "Deleted sample for id [{}]".format(id)}
        else:
            return {"status": "Error while deleting id [{}]".format(id)}
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to delete Sample with error: ', e)


def get_analysis_comments(analysis_id):
    """
    Returns list of comments for individual analysis
    """
    results = None

    try:
        results = AnalysisComment.query \
            .with_entities(AnalysisComment) \
            .filter_by(analysis_id=analysis_id) \
            .order_by(AnalysisComment.created_on.desc()) \
            .all()
    except Exception as e:
        logger.error('An error occurred in get Comments for Analysis query : {}'
                     .format(str(e)))
        raise Exception(
            'Failed to get Comments for Analysis as error in query: ', e)

    result_list = []

    if results:

        for analysis_comment in results:
            result_list.append(analysis_comment.as_dict())

    return result_list


def add_analysis_comments(analysis_id, params):
    """
    Adds Comment for particular analysis
    """
    try:
        analysis_comment = AnalysisComment(params['comment'], analysis_id,
                                           params['username'],
                                           params['username'])
        db_util.db_add_query(analysis_comment)
        db_util.db_commit()
        logger.info("Comment record for analysis id [{}] added "
                    "successfully.".format(analysis_id))

        return "Successfully added comment for analysis {}".format(analysis_id)

    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to add Comments for Analysis as error in '
                        'query: ', e)


def get_sample_primary_id(sample_id):
    result = Sample.query \
        .with_entities(Sample.id) \
        .filter_by(sample_id=sample_id) \
        .one_or_none()

    if result:
        return result.id


def get_prim_map_id(construct_id):
    map_id_result = Map.query.with_entities(Map.id) \
        .filter_by(construct_id=construct_id) \
        .one_or_none()
    if map_id_result:
        return map_id_result.id
    else:
        logger.error(
            'construct_id: {} does not exists'.format(construct_id))
        return None


def get_junctions_query(analysis_id, map_id):
    query = Analysis.query \
        .with_entities(Analysis.id,
                       Junction,
                       MapAnalysisJunctions.masked.label("masked"),
                       MapAnalysisJunctions.masked_by.label("masked_by"),
                       MapAnalysisJunctions.junction_comment.label("comment")) \
        .outerjoin(Analysis.map_analysis) \
        .outerjoin(MapAnalysis.map_analysis_junctions) \
        .outerjoin(MapAnalysisJunctions.junction) \
        .outerjoin(Map) \
        .filter(MapAnalysis.analysis_id == analysis_id) \
        .filter(Map.id == MapAnalysis.map_id) \
        .order_by(Junction.position.asc()) \
        .order_by(Junction.unique_reads.desc()) \
        .order_by(Junction.supporting_reads.desc()) \
        .order_by(Junction.junction_sequence) \
        .filter(MapAnalysis.map_id == map_id)

    return query


def get_all_junctions(analysis_id, construct_id):
    try:
        map_id = get_prim_map_id(construct_id)
        query = get_junctions_query(analysis_id, map_id)
        junctions = query.all()
    except Exception as e:
        logger.error('An error occurred in getting junction info query : {}'
                     .format(str(e)))
        raise Exception('Failed to get Junctions info as error in query: ', e)

    return junctions


def get_endogenous_junctions(analysis_id, construct_id):
    try:
        map_id = get_prim_map_id(construct_id)

        query = get_junctions_query(analysis_id, map_id)
        query = query.filter(Junction.endogenous)

        junctions = query.all()
    except Exception as e:
        logger.error('An error occurred in getting junction info query : {}'
                     .format(str(e)))
        raise Exception('Failed to get Junctions info as error in query: ', e)

    return junctions


def get_up_junctions(analysis_id, construct_id):
    try:
        map_id = get_prim_map_id(construct_id)

        query = get_junctions_query(analysis_id, map_id)
        query = query.filter(~Junction.endogenous)

        junction = query.all()
    except Exception as e:
        logger.error('An error occurred in getting junction info query : {}'
                     .format(str(e)))
        raise Exception('Failed to get Junctions info as error in query: ', e)

    return junction


def set_prev_next_sample(sample_dict):
    sample = {}
    sample['analysis_id'] = sample_dict['analysis_id']
    sample['sample_id'] = sample_dict['sample_id']
    sample['id'] = sample_dict['id']

    return sample


def get_organism(organism_id):
    try:
        crop = Crop.query \
            .with_entities(Crop.organism) \
            .filter_by(id=organism_id) \
            .one_or_none()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to get organism_id with error: ', e)

    if crop:
        return crop.organism


def set_sample_analysis_records(sample, analysis):
    sample.analysis_geno_type = analysis.geno_type
    sample.backbone_call = analysis.backbone_call
    sample.analysis_event_id = analysis.event_id
    sample.comments = get_analysis_comments(analysis.id)


def set_sample_request_records(sample, request):
    sample.req_id = request.request_id
    sample.researcher = request.researcher
    sample.request_name = request.request_name
    sample.request_organism = get_organism(request.organism_id)


def get_sample_details(params):
    """
    Provides sample response with particular project_id, sample_id and analysis_id
    """
    results = None
    request_id = params['request_id']
    sample_id = params['sample_id']
    request_primary_id = None
    try:
        # get individual sample/analysis record
        request_object = req_svc.get_request_object(request_id)

        if request_object:
            request_primary_id = request_object.id

        sample_primary_id = get_sample_primary_id(sample_id)

        if request_primary_id and sample_primary_id:
            params['request_id'] = request_primary_id
            params['sample_id'] = sample_primary_id
            query = req_svc.get_sample_query_filters(params,
                                                     req_svc.get_samples_query())
            results = query.order_by(Sample.id).all()
    except Exception as e:
        logger.error('An error occurred in getting sample info query : {}'
                     .format(str(e)))
        raise Exception('Failed to get Sample info as error in query: ', e)

    sample = {}
    constructs = {'primary_map': '', 'secondary_maps': ''}
    role = params['role']

    if not results:
        # If no result found then it will provide the previous and
        # next sample/analysis ids
        sample = get_previous_next_sample(sample, request_id,
                                          params['sample_id'],
                                          params['analysis_id'], role,
                                          params['filter_type'])

    else:
        sample = get_sample(results, request_object)
        sample = get_previous_next_sample(sample, request_id, sample['id'],
                                          sample['analysis_id'], role,
                                          params['filter_type'])

        # get junctions without endogenous junctions
        constructs = sample['construct_ids']

        junctions = get_junctions(sample['sample_id'],
                                  params['analysis_id'],
                                  constructs['primary_map'])

        sample.update(junctions)

    return sample


def get_junctions(sample_id, analysis_id, construct_id):
    junctions = {}

    up_junctions = get_up_junctions(analysis_id, construct_id)

    # setting junction response
    junctions['junctions'] = []

    if up_junctions:
        junctions['junctions'] = get_duplicate_junctions(up_junctions,
                                                         sample_id)

    # Get Endogenous junctions
    endo_junctions = get_endogenous_junctions(analysis_id, construct_id)
    junctions['endogenous_junctions'] = endo_junctions_as_dict(endo_junctions)

    return junctions


def endo_junctions_as_dict(junctions):
    """
    Gets junctions and duplicate junctions result for a sample
    """
    junction_list = []

    for result in junctions:
        junction = result[1]

        junction.masked = result.masked
        junction.masked_by = result.masked_by
        junction.comment = result.comment

        junction_list.append(junction.browse_junction_as_dict())

    return junction_list


def get_duplicate_junctions(junction_results, sample_id):
    """
    Gets junctions and duplicate junctions result for a sample
    """
    junction_list = []

    for result in junction_results:
        junction = result[1]

        if junction:
            duplicate_junctions = Request.query \
                .with_entities(Sample.sample_id.distinct().label("sample_id"),
                               Request.request_id.label("request_id"),
                               Analysis.id.label("analysis_id"),
                               Junction.position.label("junction_position")) \
                .outerjoin(Request.samples) \
                .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
                .outerjoin(Analysis.map_analysis) \
                .outerjoin(MapAnalysis.map_analysis_junctions) \
                .outerjoin(MapAnalysisJunctions.junction) \
                .filter(MapAnalysisJunctions.junction_id == junction.id) \
                .filter(Sample.sample_id != sample_id) \
                .all()

            sample_id_list = []
            if duplicate_junctions:
                for junctions in duplicate_junctions:
                    sample_id_list.append(
                        {'request_id': junctions.request_id,
                         'sample_id': junctions.sample_id,
                         'analysis_id': junctions.analysis_id,
                         'junction_position': junctions.junction_position})

            junction.masked = result.masked
            junction.masked_by = result.masked_by
            junction.comment = result.comment
            junction.duplicates_dict = {'count': len(sample_id_list),
                                        'dup_sample_ids': sample_id_list}
            junction_list.append(junction.browse_junction_as_dict())

    return junction_list


def batch_update_visible_to_client(analysis_id_list,
                                   is_visible_to_client=False):
    mappings = []

    for analysis_id in analysis_id_list:

        if is_visible_to_client:

            try:
                result = Analysis.query.with_entities(
                    Analysis.sample_id) \
                    .filter_by(id=analysis_id) \
                    .one()
            except Exception as e:
                logger.error('An error occurred in getting sample_id for '
                             'Analysis as error in query: {}'.format(str(e)))
                raise Exception('Failed to sample_id for particular Analysis '
                                'as error in query: ', e)

            sample_id = result.sample_id

            try:
                analysis = Analysis.query.with_entities(
                    Analysis.id) \
                    .filter_by(sample_id=sample_id) \
                    .filter_by(is_visible_to_client=True) \
                    .one_or_none()
            except Exception as e:
                logger.error('An error occurred in getting Analysis info query'
                             'query : {}'.format(str(e)))
                raise Exception(
                    'Failed to get Analysis info as error in query: ', e)

            if analysis:
                mappings.append(
                    dict(id=analysis.id, is_visible_to_client=False))

        mappings.append(
            dict(id=analysis_id, is_visible_to_client=is_visible_to_client))

    try:
        if mappings:
            db_util.bulk_update_mappings(Analysis, mappings)
            logger.info("record updated successfully")
        else:
            return False
    except Exception as e:
        logger.error('Failed to batch update Analysis records with error: {}'
                     .format(str(e)))
        raise Exception('Error occurred: {}'.format(e))
    return True


def get_integrity_and_junction_url(bucket, file_path, integrity, junction,
                                   sample_id):
    integrity_url = ''
    junction_url = ''
    integrity_report_file = ''
    junction_file = ''

    if integrity and integrity.lower() == 'true':
        for obj in bucket.objects.filter(Prefix=file_path):

            if obj.key.endswith('integrity.report.txt'):
                file_name = os.path.basename(obj.key)
                integrity_dir = re.match(
                    '(.*)integrity(.*)integrity.report.txt',
                    obj.key)
                observed_map = re.match('(.*){}(.*){}(.*)integrity.report.txt'
                                        .format(sample_id, sample_id),
                                        file_name)

                if not integrity_dir and not observed_map:
                    integrity_report_file = obj.key

    if junction and junction.lower() == 'true':
        try:
            sample = Sample.query.filter_by(sample_id=sample_id) \
                .one_or_none()
        except Exception as e:
            logger.error('An error occurred : {}'.format(str(e)))
            raise Exception('Failed to get Sample with error: ', e)

        if sample:
            construct_name = sample.construct_name

            for obj in bucket.objects.filter(Prefix=file_path):

                if obj.key.endswith(construct_name + '.junctions.txt'):
                    junction_file = obj.key

    try:
        integrity_url = jbrowse_svc.get_s3_presigned_url \
            (cfg.s3_bucket, integrity_report_file, '10')
    except Exception as e:
        Exception('Failed to get url: ', e)

    try:
        junction_url = jbrowse_svc.get_s3_presigned_url(cfg.s3_bucket,
                                                        junction_file, '10')
    except Exception as e:
        Exception('Failed to get url: ', e)

    return integrity_url, junction_url


def get_reports(params):
    """
    Provides pre signed url for different types of reports
    """
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    request_id = params['sample_id'][:5]
    file_path = os.path.join(cfg.s3_samples_key, request_id,
                             params['sample_id'], params['analysis_id'],
                             'output')
    bucket = s3.Bucket(name=cfg.s3_bucket)

    integrity_url, junction_url = get_integrity_and_junction_url \
        (bucket, file_path, params['integrity'], params['junction'],
         params['sample_id'])

    return {'integrity_url': integrity_url,
            'junction_url': junction_url}


def get_multiple_reports(params):
    """
    Provides presigned url for multiple sample_id and analysis_id of reports
    """
    reports = []
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    bucket = s3.Bucket(name=cfg.s3_bucket)
    integrity = params.get('integrity', '')
    junction = params.get('junction', '')

    for ids in params['sample_id_analysis_id_list']:
        request_id = str(ids['sample_id'])[:5]
        file_path = os.path.join(cfg.s3_samples_key, request_id,
                                 str(ids['sample_id']),
                                 str(ids['analysis_id']), 'output')
        integrity_url, junction_url = get_integrity_and_junction_url \
            (bucket, file_path, integrity, junction, ids['sample_id'])
        result = {'sample_id': ids['sample_id'],
                  'analysis_id': ids['analysis_id'],
                  'integrity_url': integrity_url,
                  'junction_url': junction_url}
        reports.append(result)

    return reports


def get_previous_next_sample(sample, request_id, sample_id, analysis_id, role,
                             filter_type=None):
    # get all sample/analysis records
    all_samples = req_svc.get_samples(request_id, role, filter_type)
    # get total_sample_counts
    total_samples = all_samples['total_samples']
    sample['metadata'] = {}
    sample['metadata']['total_samples'] = total_samples
    # get nth sample in all samples record
    sample_index = 0
    prev_sample_index = 0
    next_sample_index = 0
    if all_samples['result']:

        for index, sample_dict in enumerate(all_samples['result']):
            if sample_dict['id'] and sample_id and sample_dict[
                'analysis_id'] and analysis_id:
                if str(sample_dict['id']) == str(sample_id) and \
                                str(sample_dict['analysis_id']) == str(
                            analysis_id):
                    sample_index = index
                    sample['metadata']['index'] = sample_index + 1

        # get previous and next sample/analysis record
        prev_flag = True
        next_flag = True
        prev_sample = {}
        next_sample = {}
        if filter_type == 'alpha' or filter_type == 'delta':
            prev_sample_index = sample_index
            while prev_flag:
                prev_obj_type = None
                if len(all_samples['result']) > prev_sample_index > 0:
                    prev_obj_type = \
                        all_samples['result'][prev_sample_index - 1][
                            'type'].lower()
                elif prev_sample_index == 0:
                    break

                if prev_obj_type == 'alphad':
                    prev_obj_type = 'alpha'
                if len(all_samples['result']) > prev_sample_index > 0 and \
                                prev_obj_type == filter_type:
                    prev_obj = all_samples['result'][prev_sample_index - 1]
                    prev_sample = set_prev_next_sample(prev_obj)
                    prev_flag = False

                prev_sample_index -= 1
        else:
            if len(all_samples['result']) > sample_index > 0:
                prev_obj = all_samples['result'][sample_index - 1]
                prev_sample = set_prev_next_sample(prev_obj)

        next_idx = sample_index + 1
        next_sample_index = sample_index + 1
        if filter_type == 'alpha' or filter_type == 'delta':
            while next_flag:
                next_obj_type = None
                if next_sample_index < len(all_samples['result']):
                    next_obj_type = all_samples['result'][next_sample_index][
                        'type'].lower()
                elif next_sample_index == len(
                        all_samples['result']) - 1 or next_sample_index == len(
                    all_samples['result']):
                    break

                if next_obj_type == 'alphad':
                    next_obj_type = 'alpha'
                if next_obj_type == filter_type:
                    if next_sample_index < len(all_samples['result']):
                        next_obj = all_samples['result'][next_sample_index]
                        next_sample = set_prev_next_sample(next_obj)
                    next_flag = False

                next_sample_index += 1
        else:
            if next_idx < len(all_samples['result']):
                next_obj = all_samples['result'][next_idx]
                next_sample = set_prev_next_sample(next_obj)

        sample['metadata']['previous_sample'] = prev_sample
        sample['metadata']['next_sample'] = next_sample

    return sample


def get_primary_secondary_construct_list(sample_id, analysis_id):
    results = ''
    primary_map = {}
    secondary_map_dict_list = []
    try:
        results = Sample.query \
            .with_entities(Sample,
                           MapAnalysis.id.label("map_analysis_id"),
                           Map.construct_id.label("map")
                           ) \
            .filter_by(sample_id=sample_id) \
            .filter(Analysis.id == analysis_id) \
            .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
            .outerjoin(MapAnalysis) \
            .outerjoin(Map).all()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Exception occurred while fetching maps :', e)

    if results:
        for result in results:
            sample = result[0]
            if sample:
                primary_construct_name = sample.construct_name
                if result.map and result.map == primary_construct_name:
                    primary_map = {"construct_name": result.map,
                                   "map_analysis_id": result.map_analysis_id}
                else:
                    secondary_map_dict_list.append(
                        {"construct_name": result.map,
                         "map_analysis_id": result.map_analysis_id})

    return {"primary_map": primary_map,
            "secondary_maps": secondary_map_dict_list}


def get_sample(results, request):
    sample = {}
    constructs = {'primary_map': '', 'secondary_maps': ''}
    secondary_maps_list = []
    for result in results:
        sample = result[0]
        analysis = result[1]

        if sample:
            constructs['primary_map'] = sample.construct_name

            if result.map:
                secondary_maps = req_svc.get_values(result.map.split(','))

                if sample.construct_name in secondary_maps:
                    secondary_maps.remove(sample.construct_name)

                if secondary_maps:
                    for map in secondary_maps:
                        if map.startswith(sample.construct_name):
                            continue
                        secondary_maps_list.append(map)

                constructs['secondary_maps'] = secondary_maps_list

            sample.construct_ids = constructs

            if analysis:
                req_svc.set_sample_records(result, sample, analysis)
                set_sample_analysis_records(sample, analysis)

            if request:
                set_sample_request_records(sample, request)

            sample = sample.browse_sample_as_dict()

    return sample
