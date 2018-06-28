import logging

import sbs.database_utility as db_util
from sbs.models.Analysis import Analysis
from sbs.models.Map import Map
from sbs.models.MapAnalysis import MapAnalysis
from sbs.models.ObservedMap import ObservedMap
from sbs.models.ObservedMapComment import ObservedMapComment
from sbs.models.Sample import Sample
from sbs.service import analysis_service as analysis_svc
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

SUCCESS = True


def get_observed_maps(analysis_id):
    observed_maps_list = []
    is_send_to_evman = False
    highest_version = 0
    try:
        query = get_sample_query_filters(analysis_id, get_observed_map_query())
        results = query.order_by(ObservedMap.version.desc()).all()
        for result in results:
            observed_map = result[0]
            if observed_map.send_to_evman:
                is_send_to_evman = True
            observed_map.sample_id = result.sample_id
            observed_map.sample_name = result.sample_name
            observed_map.event_id = result.event_id
            observed_map.analysis_type = result.type.value
            observed_map.map_name = result.map_name
            observed_maps_list.append(observed_map.browse_as_dict())
    except Exception as e:
        logger.error('An error occurred in getting observed_maps info '
                     'query : {}'.format(str(e)))
        raise Exception('Failed to get observed_maps info as error in '
                        'query: ', e)

    process_send_to_evman(is_send_to_evman, observed_maps_list, analysis_id)

    return observed_maps_list


def process_send_to_evman(is_send_to_evman, observed_maps_list, analysis_id):
    highest_version = 0

    if is_send_to_evman:
        return observed_maps_list
    else:
        if observed_maps_list:
            observed_map_to_update = None
            for observed_map in observed_maps_list:

                if observed_map['name'].lower() == 'automatic' \
                        and observed_map['status'].lower() == 'ignore':
                    try:
                        current_version = int(observed_map['map_name']
                                              .split(".")[-1])
                    except ValueError as e:
                        logger.error("Not a valid value of version {}"
                                     .format(str(e)))
                        return

                    if highest_version < current_version:
                        highest_version = current_version
                        observed_map_to_update = observed_map

            if observed_map_to_update:
                observed_map_to_update['send_to_evman'] = True
                params = {'send_to_evman': True,
                          'construct_id': observed_map_to_update['map_name'],
                          'analysis_id': analysis_id,
                          'sample_id': observed_map_to_update['sample_id']
                          }
                try:
                    add_observed_map(params)
                except Exception as e:
                    logger.error("Failed to update Observed Map {}"
                                 .format(str(e)))
                    raise Exception("Failed to update Observed Map", e)


def get_observed_map_query():
    query = ObservedMap.query \
        .with_entities(ObservedMap,
                       Sample.sample_id.label("sample_id"),
                       Sample.sample_name.label("sample_name"),
                       Sample.event_id.label("event_id"),
                       Analysis.type.label("type"),
                       Map.construct_id.label("map_name")) \
        .outerjoin(Map) \
        .outerjoin(MapAnalysis) \
        .outerjoin(Analysis) \
        .outerjoin((Sample, Sample.id == Analysis.sample_id)) \
        .filter(ObservedMap.status != 'pending')

    return query


def get_sample_query_filters(analysis_id, query):
    if analysis_id:
        query = query.filter(Analysis.id == analysis_id)
    return query


def add_record(observed_map):
    try:
        db_util.db_add_query(observed_map)
        db_util.db_commit()
        logger.info("Observed Map added successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to add Observed Map with error: ', e)

    return observed_map


def update_record(observed_map, params):
    try:
        observed_map.name = params.get('name', observed_map.name)
        observed_map.status = params.get('status', observed_map.status)
        observed_map.load_time = params.get('load_time', observed_map.load_time)
        observed_map.length = params.get('length', observed_map.length)
        observed_map.send_to_evman = params.get('send_to_evman',
                                                observed_map.send_to_evman)
        db_util.db_commit()
        logger.info("Observed Map record updated successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update Observed Map with error: ', e)

    return observed_map


def add_observed_map(params):
    """
    Adds/Updates Observed Map
    """
    try:
        map = analysis_svc.add_map(params)
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to get Map Id for observed maps with error: ', e)

    map_id = map.id
    map_obs_map_ver = map.obs_map_version

    try:
        analysis_svc.add_map_analysis(params['analysis_id'], map_id, None)
        logger.info("Successfully added Map Analysis for analysis_id {}".format(params['analysis_id']))
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to get Map Id for observed maps with error: ', e)

    observed_map = ObservedMap.query \
        .with_entities(ObservedMap) \
        .outerjoin(Map) \
        .outerjoin(MapAnalysis) \
        .filter(ObservedMap.map_id == map_id) \
        .filter(Map.id == ObservedMap.map_id) \
        .filter(MapAnalysis.analysis_id == params['analysis_id']) \
        .one_or_none()

    if observed_map:
        observed_map = update_record(observed_map, params)
    else:
        status = params.get('status', None)
        if not status:
            status = 'pending'
        name = params.get('name', None)
        load_time = params.get('load_time', None)
        length = params.get('length', None)
        send_to_evman = params.get('send_to_evman', False)

        observed_map = ObservedMap(name, load_time, length, status,
                                   send_to_evman, map_id, map_obs_map_ver)
        observed_map = add_record(observed_map)

    observed_map.construct_id = map.construct_id
    observed_map.sample_id = params['sample_id'] 
    observed_map.analysis_id = params['analysis_id'] 

    return observed_map


def delete_observed_map(observed_map_id):
    """
    Delete Observed Map
    """
    try:
        ObservedMap.query.filter_by(id=observed_map_id).delete()
        db_util.db_commit()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to delete ObservedMap with error: ', e)


def get_observed_map_comment(observed_map_id):
    """
    Returns list of comments for individual Observed Map
    """
    observed_map_comments = None

    try:
        observed_map_comments = ObservedMap.query \
            .with_entities(ObservedMapComment) \
            .filter_by(observed_map_id=observed_map_id) \
            .order_by(ObservedMapComment.created_on.desc()) \
            .all()
    except Exception as e:
        logger.error(
            'An error occurred in get Comments for Observed Map query : {}'
                .format(str(e)))
        raise Exception(
            'Failed to get Comments for Observed Map as error in query: ', e)

    return observed_map_comments


def add_observed_map_comments(observed_map_id, params):
    """
    Adds Comment for particular ObservedMap
    """
    try:
        observed_map_comment = ObservedMapComment(params['comment'],
                                                  observed_map_id,
                                                  params['username'],
                                                  params['username'])
        db_util.db_add_query(observed_map_comment)
        db_util.db.session.commit()
        observed_map_comment = observed_map_comment.as_dict()
        db_util.db.session.close()
    except Exception as e:
        logger.error('Failed to add ObservedMap comments with error: {}'
                     .format(str(e)))
        raise Exception('Failed to add Comments for ObservedMap as error in '
                        'query: ', e)
    logger.info("Comment record for ObservedMap id [{}] added successfully."
                .format(observed_map_id))

    return observed_map_comment
