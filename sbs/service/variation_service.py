import logging

import sbs.database_utility as db_util
from sbs.models.Sample import Sample
from sbs.models.Analysis import Analysis
from sbs.models.Map import Map
from sbs.models.ObservedMap import ObservedMap
from sbs.models.MapAnalysis import MapAnalysis
from sbs.models.Variation import Variation
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def get_variation_by_construct(analysis_id, construct_id):
    try:
        map_id_result = Map.query.with_entities(Map.id) \
            .filter_by(construct_id=construct_id) \
            .one_or_none()
        if map_id_result:
            map_id = map_id_result.id
        else:
            logger.error('construct_id: {} does not exists'.format(construct_id))
            return
        variation = Analysis.query \
            .with_entities(Analysis.id, Variation) \
            .outerjoin(Analysis.map_analysis) \
            .outerjoin(MapAnalysis.variation) \
            .outerjoin(Map) \
            .filter(MapAnalysis.analysis_id == analysis_id) \
            .filter(Map.id == MapAnalysis.map_id) \
            .filter(MapAnalysis.map_id == map_id).all()
    except Exception as e:
        logger.error('An error occurred in getting variation info query : {}'
                     .format(str(e)))
        raise Exception('Failed to get variation info as error in query: ', e)

    return variation


def get_map_primary_id(construct_id):
    map_id_result = Map.query.with_entities(Map.id) \
        .filter_by(construct_id=construct_id) \
        .one_or_none()
    if map_id_result:
        map_id = map_id_result.id
    else:
        logger.error('construct_id: {} does not exists'.format(construct_id))
        return

    return map_id


def get_integrities(analysis_id, map_id=None):
    results = None
    try:
        if map_id:
            # Gets observed maps integrities data
            query = get_variation_query_filters(analysis_id, get_variation_query().outerjoin(ObservedMap)) \
                    .filter(Map.id == ObservedMap.map_id) \
                    .filter(MapAnalysis.map_id == Map.id) \
                    .filter(Map.construct_id == map_id)
            query = sort_integrities(query)
        else:
            # Gets expected maps integrities data
            primary_construct = get_primary_construct(analysis_id)
            if primary_construct:
                map_id = get_map_primary_id(primary_construct)
                query = get_variation_query_filters(analysis_id, get_variation_query()) \
                        .filter(MapAnalysis.map_id == map_id)
                query = sort_integrities(query)

        results = query.all()
    except Exception as e:
        logger.error('Failed to get integrity as error in query:  {}'
                     .format(str(e)))
        raise Exception('An error occurred in get all integrity query :', e)

    result_list = []

    if results:
        for result in results:
            variation = result[0]
            construct_id = result[1]
            if variation:
                variation.construct_id = construct_id
                result_list.append(variation)

    return result_list


def get_variation_query():
    query = Variation.query \
        .with_entities(Variation,
                       Map.construct_id.label('construct_id')
                       ) \
        .outerjoin(MapAnalysis) \
        .outerjoin(Map)
    return query


def get_variation_query_filters(analysis_id, query):
    if analysis_id:
        query = query \
                .filter(MapAnalysis.analysis_id == analysis_id) \
                .filter(MapAnalysis.map_id == Map.id) \
                .filter(MapAnalysis.id == Variation.map_analysis_id)
    return query


def sort_integrities(query):
    query = query.order_by(Variation.position.asc()) \
                 .order_by(Variation.purity.desc())
    return query


def get_primary_construct(analysis_id):
    primary_construct = ""
    try:
        query = Sample.query \
                .with_entities(Sample.construct_name.label('construct_name')) \
                .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
                .filter(Analysis.id == str(analysis_id))
        result = query.all()
        if result:
            primary_construct = result[0].construct_name
    except Exception as e:
        logger.error('An error occurred in getting primary construct with error'
                     .format(str(e)))
        raise Exception('Failed to get primary construct as error in query: ', e)
        
    return primary_construct


def batch_update_tier(variation_list):
    """
    Change tier_label for single or multiple variations
    """
    variation_mapping = []

    if variation_list:
        for variation in variation_list:
            variation_mapping.append(dict(id=variation['variation_id'],
                                          tier_label=variation['tier_label'],
                                          is_tier_label_updated=True))

        try:
            db_util.bulk_update_mappings(Variation, variation_mapping)
            logger.info("Variation record updated successfully.")
        except Exception as e:
            logger.error('Failed to batch update Variation records with error'
                         ': {}'.format(str(e)))
            raise Exception('Error occurred: {}'.format(e))

        return variation_mapping
