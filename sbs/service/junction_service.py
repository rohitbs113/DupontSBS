import logging

from sqlalchemy import distinct

import sbs.database_utility as db_util
from sbs.models.Analysis import Analysis
from sbs.models.EndogenousJunction import EndogenousJunction
from sbs.models.EndogenousJunctionSet import EndogenousJunctionSet
from sbs.models.Junction import Junction
from sbs.models.MapAnalysisJunctions import MapAnalysisJunctions
from sbs.models.PipelineConfiguration import PipelineConfiguration
from sbs.service import sample_service, request_service
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

SUCCESS = True


def set_boolean_junction_values(junction_val):
    bool_val = False
    if junction_val == '' or junction_val == 'False':
        bool_val = False
    else:
        bool_val = True

    return bool_val


def insert_junctions(junctions_dict_list):
    """
    Adds JUNCTION records
    """
    try:
        for junction in junctions_dict_list:
            if junction:
                if 'map_analysis_id' not in junction or not junction[
                    'map_analysis_id']:
                    logger.error('map_analysis_id is required')
                    raise Exception('map_analysis_id is required in junction')
                map_analysis_id = junction['map_analysis_id']
                masked = junction['masked']
                masked = set_boolean_junction_values(masked)
                endogenous = junction['endogenous']
                endogenous = set_boolean_junction_values(endogenous)
                junction['endogenous'] = endogenous
                junction, is_duplicate = get_duplicate_junctions(junction)
                if is_duplicate:
                    try:
                        junction_id = junction.id
                        save_map_analysis_junctions(map_analysis_id,
                                                    junction_id, masked)
                    except Exception as e:
                        logger.error('An error occurred : {}'.format(str(e)))
                        raise Exception(
                            'Failed to insert map_analysis_junction records with error: {}'.format(
                                e))
                elif not is_duplicate:
                    try:
                        end = junction.get('end', None)
                        position = junction.get('position', None)
                        proximal_mapping = junction.get('proximal_mapping',
                                                        None)
                        if proximal_mapping == "NA" or not proximal_mapping:
                            proximal_percent_identity = None
                        else:
                            proximal_percent_identity = proximal_mapping \
                                .split(",")[-1]

                        proximal_sequence = junction.get('proximal_sequence',
                                                         None)
                        junction_sequence = junction.get('junction_sequence',
                                                         None)
                        proximal_sequence_length = junction.get(
                            'proximal_sequence_length', None)
                        distal_sequence = junction.get('distal_sequence', None)
                        distal_mapping = junction.get('distal_mapping', None)

                        if distal_mapping == "NA" or not distal_mapping:
                            distal_percent_identity = None
                        else:
                            distal_percent_identity = distal_mapping \
                                .split(",")[-1]

                        distal_sequence_length = junction.get(
                            'distal_sequence_length', None)
                        element = junction.get('element', None)
                        unique_reads = junction.get('unique_reads', None)
                        supporting_reads = junction.get('supporting_reads',
                                                        None)
                        endogenous = junction.get('endogenous', endogenous)
                        source = junction.get('source', None)
                        duplicates = junction.get('duplicates', None)
                        junction_record = Junction(end, position,
                                                   proximal_mapping,
                                                   proximal_percent_identity,
                                                   proximal_sequence,
                                                   junction_sequence,
                                                   proximal_sequence_length,
                                                   distal_sequence,
                                                   distal_mapping,
                                                   distal_percent_identity,
                                                   distal_sequence_length,
                                                   element, unique_reads,
                                                   supporting_reads,
                                                   endogenous, source,
                                                   duplicates)
                        db_util.db_add_query(junction_record)
                        db_util.db_commit()
                        logger.info(
                            "Junction record for added successfully {}".format(
                                junction_record))

                        junction_id = junction_record.id
                        save_map_analysis_junctions(map_analysis_id,
                                                    junction_id, masked)
                    except Exception as e:
                        logger.error('An error occurred : {}'.format(str(e)))
                        raise Exception(
                            'Failed to insert map_analysis_junction records with error: {}'.format(
                                e))
                else:
                    logger.info("something went wrong")
        logger.info("Junction record added successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception(
            'Failed to batch insert Junction records with error: {}'.format(e))
    return SUCCESS


def update_junction_mask(junctions_dict_list, is_masked, junction_comment,
                         masked_by, curr_construct_name,
                         curr_sample_id,
                         analysis_id):
    try:
        map_dict = sample_service.get_primary_secondary_construct_list(
            curr_sample_id, analysis_id)
        primary_construct_name = map_dict['primary_map']['construct_name']
        primary_map_analysis_id = map_dict['primary_map']['map_analysis_id']
        secondary_constructs = map_dict['secondary_maps']
        if primary_construct_name == curr_construct_name:
            update_map_analysis_jn(secondary_constructs, junctions_dict_list,
                                   is_masked,
                                   "Identical to Primary Junction {}",
                                   masked_by, True)
            update_map_analysis_jn(
                [{'map_analysis_id': primary_map_analysis_id}],
                junctions_dict_list, is_masked,
                junction_comment, masked_by, False)
        else:
            for map in secondary_constructs:
                if map['construct_name'] == curr_construct_name:
                    update_map_analysis_jn([map], junctions_dict_list,
                                           is_masked, junction_comment,
                                           masked_by, False)
        logger.info("Junction record updated successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception(
            'Failed to batch updated Junction records with error: {}'.format(e))
    return SUCCESS


def get_duplicate_junctions(junction):
    is_duplicate = False
    try:
        duplicate_junction = Junction.query \
            .with_entities(Junction.id, Junction) \
            .filter(Junction.end == junction['end']) \
            .filter(Junction.position == junction['position']) \
            .filter(Junction.proximal_mapping == junction['proximal_mapping']) \
            .filter(Junction.proximal_sequence == junction['proximal_sequence']) \
            .filter(Junction.junction_sequence == junction['junction_sequence']) \
            .filter(Junction.proximal_sequence_length == junction[
            'proximal_sequence_length']) \
            .filter(Junction.distal_sequence == junction['distal_sequence']) \
            .filter(Junction.distal_mapping == junction['distal_mapping']) \
            .filter(Junction.distal_sequence_length == junction[
            'distal_sequence_length']) \
            .filter(Junction.element == junction['element']) \
            .filter(Junction.unique_reads == junction['unique_reads']) \
            .filter(Junction.supporting_reads == junction['supporting_reads']) \
            .filter(Junction.endogenous == junction['endogenous']) \
            .filter(Junction.source == junction['source']) \
            .filter(Junction.duplicates == junction['duplicates']) \
            .one_or_none()

        if duplicate_junction:
            is_duplicate = True
            return duplicate_junction, is_duplicate
        else:
            return junction, is_duplicate
    except Exception as e:
        logger.error('An error occurred in get duplicate junctions query : {}'
                     .format(str(e)))
        raise Exception('Failed to get duplicate junctions as error in query: ',
                        e)


def update_map_analysis_jn(constructs, junctions_dict_list, is_masked, comment,
                           masked_by, is_duplicate):
    for junction in junctions_dict_list:
        for map in constructs:
            map_analysis_jn = MapAnalysisJunctions.query.filter_by(
                junction_id=junction['id']).filter_by(
                map_analysis_id=map['map_analysis_id']).one_or_none()
            if map_analysis_jn and map_analysis_jn.masked != is_masked:
                map_analysis_jn.masked = is_masked
                if is_duplicate and is_masked:
                    map_analysis_jn.junction_comment = comment.format(
                        junction['position'])
                elif is_duplicate and not is_masked:
                    map_analysis_jn.junction_comment = None
                else:
                    map_analysis_jn.junction_comment = comment
                map_analysis_jn.masked_by = masked_by
                db_util.db_commit()


def update_junction_duplicate_mask(junction_id_list, comment, curr_req_id,
                                   is_masked, masked_by):
    map_analyses = request_service.get_map_analysis_by_request(curr_req_id)
    for map_analysis_id in map_analyses:
        for jn_id in junction_id_list:
            map_analysis_jn = MapAnalysisJunctions.query.filter_by(
                junction_id=jn_id).filter_by(
                map_analysis_id=map_analysis_id[0]).one_or_none()
            if map_analysis_jn and map_analysis_jn.masked != is_masked:
                map_analysis_jn.masked = is_masked
                map_analysis_jn.junction_comment = comment
                map_analysis_jn.masked_by = masked_by
                db_util.db_commit()

    return SUCCESS


def save_map_analysis_junctions(map_analysis_id, junction_id, masked):
    try:
        map_analysis_junction = MapAnalysisJunctions.query \
            .with_entities(MapAnalysisJunctions) \
            .filter(MapAnalysisJunctions.map_analysis_id == map_analysis_id) \
            .filter(MapAnalysisJunctions.junction_id == junction_id) \
            .one_or_none()
        if not map_analysis_junction:
            map_analysis_junction = MapAnalysisJunctions(map_analysis_id,
                                                         junction_id, masked,
                                                         None,
                                                         None)
        else:
            map_analysis_junction.masked = masked

        db_util.db_add_query(map_analysis_junction)
        db_util.db_commit()
        logger.info("Record for map_analysis_junction id [{}] added "
                    "successfully.".format(junction_id))
    except Exception as e:
        logger.error(
            'An error occurred while saving map analysis junctions : {}'
                .format(str(e)))
        raise Exception('Failed to save map analysis junction : ', e)


def update_junction(junction):
    cur_junction = Junction.query \
        .filter_by(junction_id=junction['id']) \
        .one_or_none()

    if cur_junction:
        cur_junction.end = junction.get('end', cur_junction.end)
        cur_junction.position = junction.get('position', cur_junction.position)
        cur_junction.proximal_mapping = junction.get('proximal_mapping',
                                                     cur_junction.proximal_mapping)
        cur_junction.proximal_percent_identity = junction.get(
            'proximal_percent_identity', cur_junction.proximal_percent_identity)
        cur_junction.proximal_sequence = junction.get('proximal_sequence',
                                                      cur_junction.proximal_sequence)
        cur_junction.junction_sequence = junction.get('junction_sequence',
                                                      cur_junction.junction_sequence)
        cur_junction.distal_sequence = junction.get('distal_sequence',
                                                    cur_junction.distal_sequence)
        cur_junction.proximal_sequence_length = junction.get(
            'proximal_sequence_length', cur_junction.proximal_sequence_length)
        cur_junction.distal_mapping = junction.get('distal_mapping',
                                                   cur_junction.distal_mapping)
        cur_junction.distal_percent_identity = junction.get(
            'distal_percent_identity', cur_junction.distal_percent_identity)
        cur_junction.distal_sequence_length = junction.get(
            'distal_sequence_length', cur_junction.distal_sequence_length)
        cur_junction.element = junction.get('element', cur_junction.element)
        cur_junction.unique_reads = junction.get('unique_reads',
                                                 cur_junction.unique_reads)
        cur_junction.supporting_reads = junction.get('supporting_reads',
                                                     cur_junction.supporting_reads)
        cur_junction.endogenous = junction.get('endogenous',
                                               cur_junction.endogenous)
        cur_junction.source = junction.get('source', cur_junction.source)
        cur_junction.duplicates = junction.get('duplicates',
                                               cur_junction.duplicates)

    try:
        db_util.db_commit()
        logger.info("Junction record updated successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update Junction with error: ', e)

    return cur_junction


def set_endogenous_junction(junction_ids):
    """
    Add the given junction as endogenous junction and if its not present in
     Endogenous Set then add it.
    :param junction_id: 
    :return: 
    """
    if not junction_ids:
        return False

    up_junctions = []

    for junction_id in junction_ids:
        up_junctions.append(
            dict(id=junction_id, endogenous=True))

    up_endo_junctions = []
    for junction_id in junction_ids:
        up_endo_junctions.append(
            dict(id=junction_id))

    try:
        db_util.bulk_update_mappings(Junction, up_junctions)
        logger.info("Junction records updated successfully")

        db_util.bulk_insert_mappings(EndogenousJunction, up_endo_junctions)
        logger.info("Endogenous Junction records added successfully")
    except Exception as e:
        logger.error('Failed to batch update junctions with error: {}'
                     .format(str(e)))
        raise Exception('Error occurred: {}'.format(e))

        # Add this junction to endogenous set
    return True


def add_endo_junction_set(endo_set_name):
    # Add Endogenous Set record if not present
    endo_set = EndogenousJunctionSet.query \
        .filter_by(name=endo_set_name) \
        .one_or_none

    if not endo_set:
        crop_id = None
        endo_set = EndogenousJunctionSet(crop_id, endo_set_name)
        db_util.db_add_query(endo_set)
        db_util.db_commit()

    return endo_set


def update_endogenous_set(analysis_id, junction_ids):
    if not junction_ids:
        return False

    # Get Endogenous Set name
    endo_set_name = PipelineConfiguration.query \
        .with_entities(PipelineConfiguration.endogenous_set) \
        .outerjoin(Analysis) \
        .filter(Analysis.id == analysis_id) \
        .one_or_none()

    if not endo_set_name:
        return False

    endo_set = add_endo_junction_set(endo_set_name)

    # Check if sequences exists in Endogenous set
    items = EndogenousJunction.query \
        .with_entities(EndogenousJunction,
                       Junction.junction_sequence.label('seq')) \
        .filter(EndogenousJunction.junction_id.in_(junction_ids)) \
        .outerjoin(Junction) \
        .all()

    sequences = {}  # Dict of {sequence: endogenous_junction_obj}
    for item in items:
        if item.seq not in sequences.values():
            sequences[item.seq] = item[0]

    avl_endoseqs = Junction.query() \
        .with_entities(distinct(Junction.junction_sequence.label('seq'))) \
        .outerjoin(EndogenousJunction) \
        .outerjoin(EndogenousJunctionSet) \
        .filter(EndogenousJunctionSet.name == endo_set_name) \
        .filter(Junction.junction_sequence.in_(sequences)) \
        .all()

    avl_endoseqs_list = []
    for s in avl_endoseqs:
        if s.seq not in avl_endoseqs_list:
            avl_endoseqs_list.append(s.seq)

    # Update Endogenous Junction record with endo set id
    for seq in sequences.values():
        if seq not in avl_endoseqs_list:
            endo_junc = sequences[seq]
            endo_junc.junction_set = endo_set.id
            db_util.db_commit()

    return True
