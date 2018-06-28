import json
import logging

import sbs.database_utility as db_util
import sbs.service.pipeline_configuration_service as configuration_svc
from sbs.models.Analysis import Analysis
from sbs.models.Analysis import RequestType
from sbs.models.AnalysisTools import AnalysisTools
from sbs.models.AnalysisToolsDetails import AnalysisToolsDetails
from sbs.models.Map import Map
from sbs.models.MapAnalysis import MapAnalysis
from sbs.models.ObservedMap import ObservedMap
from sbs.models.Request import Request
from sbs.models.Sample import Sample
from sbs.models.Variation import Variation
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def add_analysis(params):
    """
    Adds ANALYSIS record
    """
    try:
        analysis = create_analysis(params)
        db_util.db_add_query(analysis)
        db_util.db_commit()
        logger.info("Analysis record added successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to add Analysis with error: ', e)

    return analysis


def create_analysis(params):
    try:
        sample = Sample.query.filter_by(
            sample_id=params.get('sample_id')).one_or_none()
        if sample:
            sample_id = sample.id
        else:
            raise Exception("Sample not found for sample id: {}".format(
                params.get('sample_id')))
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to get sample_id with error: ', e)

    input_map = params.get('input_map', None)
    type = params.get('type').lower()
    enum_type_value = RequestType[type].value
    reference = params.get('reference', None)
    job_status = params.get('job_status', None)
    sbs_status = params.get('sbs_status', None)
    sbs_version = params.get('sbs_version', None)
    pipeline_call = params.get('pipeline_call', None)
    current_call = params.get('current_call', None)
    geno_type = params.get('geno_type', None)
    event_id = params.get('event_id', None)
    backbone_call = params.get('backbone_call', None)
    released_on = params.get('released_on', None)
    sample_call = params.get('sample_call', None)
    sbs_integ_tier = params.get('sbs_integ_tier', None)
    vqc_ali_pct = params.get('vqc_ali_pct', None)
    complete_probe_coverage = params.get('complete_probe_coverage', None)
    target_rate = params.get('target_rate', None)
    tier_3_reason = params.get('tier_3_reason', None)
    is_deprecated = params.get('is_deprecated', False)
    is_visible_to_client = params.get('is_visible_to_client', False)
    load_date = params.get('load_date', None)
    single_read_count = params.get('single_read_count', None)
    paired_read_count = params.get('paired_read_count', None)
    manual_set = params.get('manual_set', None)
    call_comment = params.get('call_comment', None)

    try:
        if single_read_count:
            single_read_count = int(params.get('single_read_count'))
    except ValueError as e:
        logger.error('Invalid value for single read count : {}'.format(str(e)))
        raise Exception(
            'single read count value should be numeric with error: ', e)

    try:
        if paired_read_count:
            paired_read_count = int(params.get('paired_read_count'))
    except ValueError as e:
        logger.error('Invalid value for paired read count : {}'.format(str(e)))
        raise Exception(
            'paired read count value should be numeric with error: ', e)

    analysis = Analysis(input_map, enum_type_value, sample_id, reference,
                        job_status, sbs_status, sbs_version, pipeline_call,
                        current_call, geno_type, event_id, backbone_call,
                        released_on, sample_call, sbs_integ_tier, vqc_ali_pct,
                        is_deprecated, load_date, is_visible_to_client,
                        single_read_count, paired_read_count,
                        complete_probe_coverage, target_rate, tier_3_reason,
                        manual_set, call_comment)

    return analysis


def update_analysis(params):
    """
    Update ANALYSIS record
    """
    try:
        analysis_id = params.get('analysis_id', None)
        analysis = Analysis.query.filter_by(id=analysis_id).one()
        if not analysis:
            raise Exception("Failed to get Analysis record")

        analysis.input_map = params.get('input_map', analysis.input_map)
        analysis.type = params.get('type', analysis.type.value)
        analysis.reference = params.get('reference', analysis.reference)
        analysis.job_status = params.get('job_status', analysis.job_status)
        analysis.sbs_status = params.get('sbs_status', analysis.sbs_status)
        analysis.sbs_version = params.get('sbs_version', analysis.sbs_version)

        if not analysis.pipeline_call:
            analysis.pipeline_call = params.get('pipeline_call',
                                                analysis.pipeline_call)

        analysis.current_call = params.get('current_call',
                                           analysis.current_call)
        analysis.geno_type = params.get('geno_type', analysis.geno_type)
        analysis.event_id = params.get('event_id', analysis.event_id)
        analysis.backbone_call = params.get('backbone_call',
                                            analysis.backbone_call)
        analysis.released_on = params.get('released_on', analysis.released_on)
        analysis.sample_call = params.get('sample_call', analysis.sample_call)
        analysis.sbs_integ_tier = params.get('sbs_integ_tier',
                                             analysis.sbs_integ_tier)
        analysis.vqc_ali_pct = params.get('vqc_ali_pct', analysis.vqc_ali_pct)
        analysis.complete_probe_coverage = params.get('complete_probe_coverage',
                                                      analysis.complete_probe_coverage)
        analysis.target_rate = params.get('target_rate', analysis.target_rate)
        analysis.tier_3_reason = params.get('tier_3_reason',
                                            analysis.tier_3_reason)
        analysis.is_deprecated = params.get('is_deprecated',
                                            analysis.is_deprecated)
        analysis.is_visible_to_client = params.get('is_visible_to_client',
                                                   analysis.is_visible_to_client)
        analysis.load_date = params.get('load_date', analysis.load_date)
        analysis.single_read_count = params.get('single_read_count',
                                                analysis.single_read_count)
        analysis.paired_read_count = params.get('paired_read_count',
                                                analysis.paired_read_count)
        analysis.call_comment = params.get('call_comment',
                                           analysis.call_comment)

        if params.get('manual_set'):
            analysis.manual_set = params.get('manual_set', analysis.manual_set)
            analysis.current_call = params.get('manual_set',
                                               analysis.current_call)

        db_util.db_commit()
        logger.info("Analysis record updated successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update Analysis with error: ', e)

    return analysis


def batch_insert_integrities(integrities_dict_list):
    """
    Adds variation
    """
    try:
        for variation in integrities_dict_list:
            if variation:
                position = variation.get('position', None)
                type = variation.get('type', None)
                gt = variation.get('gt', None)
                ref_base = variation.get('ref_base', None)
                total_read_depth = variation.get('total_read_depth', None)
                sample_base = variation.get('sample_base', None)
                read_depth = variation.get('read_depth', None)
                purity = variation.get('purity', None)
                feature_type = variation.get('feature_type', None)
                annotation = variation.get('annotation', None)
                effects = variation.get('effects', None)
                translation = variation.get('translation', None)
                organism = variation.get('organism', None)
                tier_label = variation.get('tier_label', None)
                coverage = variation.get('coverage', None)
                tier = variation.get('tier', None)
                is_tier_label_updated = variation.get('is_tier_label_updated',
                                                      False)
                map_analysis_id = variation.get('map_analysis_id', None)
                if not check_duplicate_variation(position, type, gt, ref_base,
                                                 total_read_depth, sample_base,
                                                 read_depth, purity,
                                                 feature_type, annotation,
                                                 effects, translation,
                                                 organism, tier_label,
                                                 map_analysis_id):
                    variation = Variation(position, type, ref_base, sample_base,
                                          translation,
                                          coverage, purity, tier, read_depth,
                                          annotation, tier_label,
                                          is_tier_label_updated, gt,
                                          total_read_depth, feature_type,
                                          effects, organism, map_analysis_id)
                    db_util.db_add_query(variation)
                    db_util.db_commit()
                    logger.info("Variation record added successfully.")
    except Exception as e:
        logger.error('Failed to batch insert Variation records with error: {}'
                     .format(str(e)))
        raise Exception('Error occurred: {}'.format(e))


def get_map_by_construct_id(construct_id):
    try:
        return Map.query.filter_by(construct_id=construct_id).one_or_none()
    except Exception as e:
        logger.info(
            'failed to get map by construct id {} with error: {}'.format(
                map.construct_id, str(e)))


def add_map(params):
    """
    Adds Map
    """
    version = 0
    construct_id = params.get('construct_id', None)

    if construct_id:
        logger.info('Adding Map for construct_id [{}]'.format(construct_id))
        map = get_map_by_construct_id(construct_id)
        if map:
            logger.info('Map {} already exists'.format(map.construct_id))
            return map
    else:
        construct_id_no_ver = '.'.join([params['map_id'],
                                        params['sample_id'],
                                        '']).lower()

        obs_map_ver = ObservedMap.query \
            .with_entities(ObservedMap.version) \
            .outerjoin(Map) \
            .outerjoin(MapAnalysis) \
            .filter(MapAnalysis.analysis_id == params['analysis_id']) \
            .filter(Map.construct_id.ilike(construct_id_no_ver + '%')) \
            .order_by(ObservedMap.version.desc()) \
            .limit(1) \
            .one_or_none()

        if obs_map_ver:
            version = int(obs_map_ver[0]) + 1
        else:
            version = 1

        construct_id = construct_id_no_ver + str(version)

    try:
        map = Map(construct_id.upper())
        db_util.db_add_query(map)
        db_util.db_commit()
        if version > 0:
            map.obs_map_version = version
        logger.info("Successfully added Map {}".format(construct_id))
    except Exception as e:
        logger.error('Failed to add Map with error: {}'.format(str(e)))
        raise Exception('Failed to add Map with error: ', e)

    return map


def get_map_analysis(map_id, analysis_id):
    return MapAnalysis.query \
        .filter_by(map_id=map_id, analysis_id=analysis_id) \
        .one_or_none()


def add_map_analysis(analysis_id, map_id, read_count):
    """
    Adds Map record
    """
    logger.info('Adding MapAnalysis for map_id [{}] and analysis_id [{}]')
    map_analysis = get_map_analysis(map_id, analysis_id)
    if map_analysis:
        logger.info('MapAnalysis already exists')
        return map_analysis

    try:
        map_analysis = MapAnalysis(read_count, analysis_id, map_id)
        db_util.db_add_query(map_analysis)
        db_util.db_commit()
        logger.info("Successfully added MapAnalysis."
                    .format(analysis_id, map_id))
    except Exception as e:
        logger.error('Failed to add MapAnalysis with error: {}'.format(str(e)))
        raise Exception('Failed to add MapAnalysis with error: ', e)
    return map_analysis


def batch_update_promote_to_alpha(analysis_id_list):
    list = []
    sample_list = []
    try:
        for analysis_id in analysis_id_list:
            list.append(str(analysis_id))

        query = Analysis.query \
            .filter(Analysis.id.in_((list))) \
            .filter(Analysis.type != RequestType.delta)
        result = query.all()
        if result:
            raise Exception('List contains records other than delta')
    except Exception as e:
        logger.error('Failed to batch update Analysis records with error: {}'
                     .format(str(e)))
        raise Exception('Error occurred: {}'.format(e))

    try:
        query = Analysis.query \
            .with_entities(Analysis.id, Analysis.sample_id) \
            .filter(Analysis.id.in_((list)))
        analysis_result = query.all()
        if analysis_result:
            for result in analysis_result:
                sample_list.append(
                    dict(id=result[1], curr_alpha_analysis=result[0]))

        if sample_list:
            db_util.bulk_update_mappings(Sample, sample_list)
            logger.info("current alpha analysis record updated successfully")
    except Exception as e:
        logger.error(
            'Failed to batch update current alpha analysis record with error: {}'
                .format(str(e)))
        raise Exception('Error occurred: {}'.format(e))

    mappings = []
    for analysis_id in analysis_id_list:
        mappings.append(dict(id=analysis_id, type=RequestType.alphad))

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


def add_analysis_tools(analysis_tools):
    """
    Adds Analysis Tools record
    """
    analysis_tool_list = []
    for name in analysis_tools:
        analysis_tool = AnalysisTools.query.filter(
            AnalysisTools.name == name).one_or_none()
        if not analysis_tool:
            analysis_tool = AnalysisTools(name)
            db_util.db_add_query(analysis_tool)
    db_util.db_commit()
    # Get all the five tools records
    all_tool_records = AnalysisTools.query.all()
    for tool_obj in all_tool_records:
        analysis_tool_list.append(tool_obj)

    return analysis_tool_list


def add_tool_record(analysis_tool_details):
    db_util.db_add_query(analysis_tool_details)
    db_util.db_commit()
    return analysis_tool_details


def add_analysis_tool_details(params):
    """
    Adds Analysis Tools Details record
    """
    message = params.get('message', None)
    cna_detail = params.get('cna_detail', None)
    try:
        query = Sample.query \
            .with_entities(Sample.construct_name.label('construct_name')) \
            .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
            .filter(Analysis.id == params['analysis_id'])
        result = query.all()
        if result:
            map_name = result[0].construct_name
            map = get_map_by_construct_id(map_name)
            if not map:
                map_data = Map(map_name, cna_detail, cna_detail)
                map_response = add_tool_record(map_data)
                logger.info(json.dumps(map_response.as_dict(), indent=2))
                logger.info(
                    "Added map with pipeline and custom pipeline details successfully.")
            else:
                # Update cna_detail if MAP_ID exists with NULL CNA data
                if not map.pipeline_detail and not map.custom_pipeline_detail:
                    map.pipeline_detail = cna_detail
                    map.custom_pipeline_detail = cna_detail

        tool_details = update_analysis_tool_details(params)
        if tool_details:
            return tool_details

        else:
            # add new Analysis Tool Details record(for both pipeline and current call)
            analysis_tool_details = AnalysisToolsDetails(params['call'],
                                                         params['call'],
                                                         message, message,
                                                         cna_detail,
                                                         params['analysis_id'],
                                                         params['tool_id'])
            logger.info("Analysis Tools Details record added successfully.")
            return add_tool_record(analysis_tool_details)

    except Exception as e:
        logger.error('Failed to update tools details with error: {}'
                     .format(str(e)))
        raise Exception('Failed to update tools details with error: ', e)


def get_tool_details(tool_details):
    current_call = tool_details.current_call
    current_msg = tool_details.current_msg
    pipeline_call = tool_details.pipeline_call
    pipeline_msg = tool_details.pipeline_msg
    cna_detail = tool_details.current_detail

    return current_call, current_msg, pipeline_call, pipeline_msg, cna_detail


def get_call_details(analysis_id):
    try:
        query = Analysis.query \
            .with_entities(Analysis.created_on.label('created_on'),
                           AnalysisToolsDetails,
                           AnalysisTools.name.label('tool_name'),
                           Request.sample_prep_methods.label('prep_method'),
                           Analysis.sbs_version.label('version'),
                           Map.pipeline_detail.label('pipeline_detail'),
                           Map.custom_pipeline_detail.label(
                               'custom_pipeline_detail'),
                           Analysis.current_call.label('current_call')
                           ) \
            .outerjoin(AnalysisToolsDetails) \
            .outerjoin(AnalysisTools) \
            .outerjoin(Request.samples) \
            .outerjoin(MapAnalysis) \
            .outerjoin(Map) \
            .filter(Analysis.id == analysis_id) \
            .filter(Analysis.sample_id == Sample.id) \
            .filter(Sample.request_id == Request.id) \
            .filter(AnalysisToolsDetails.analysis_id == Analysis.id) \
            .filter(AnalysisTools.id == AnalysisToolsDetails.tool_id) \
            .filter(Map.construct_id == Sample.construct_name) \
            .filter(MapAnalysis.analysis_id == Analysis.id) \
            .filter(Map.id == MapAnalysis.map_id) \
            .group_by(AnalysisToolsDetails.id)

        result = query.all()
    except Exception as e:
        logger.error('Failed to get pipeline details with error: {}'
                     .format(str(e)))
        raise Exception('Failed to get pipeline details with error: ', e)

    response_dict = {}
    if result:
        header_data = result[0]
        response_dict['call_time'] = header_data.created_on
        response_dict['prep_method'] = header_data.prep_method
        response_dict['prep_method_version'] = header_data.version
        current_detail_list = []
        pipeline_detail_list = []

        for row in result:
            tool_details = row[1]
            analysis_current_call = row.current_call
            if tool_details:
                current_call, current_msg, pipeline_call, pipeline_msg, \
                cna_detail = get_tool_details(tool_details)

                if analysis_current_call and analysis_current_call.lower() == "pending":
                    current_call = analysis_current_call
                    current_msg = ""
                    cna_detail = ""
                tool_id = tool_details.tool_id
                current_detail_dict = dict(tool_name=row.tool_name,
                                           current_call=current_call,
                                           current_msg=current_msg,
                                           tool_id=tool_id)

                if row.tool_name == 'CopyNumberAnalysis':
                    current_detail_dict['cna_current'] = cna_detail
                    current_detail_dict['cna_pipeline'] = row.pipeline_detail
                    current_detail_dict[
                        'cna_custom'] = row.custom_pipeline_detail

                pipeline_detail_dict = dict(pipeline_call=pipeline_call,
                                            pipeline_msg=pipeline_msg,
                                            tool_name=row.tool_name,
                                            tool_id=tool_id)
                current_detail_list.append(current_detail_dict)
                pipeline_detail_list.append(pipeline_detail_dict)
                response_dict['current_details'] = current_detail_list
                response_dict['pipeline_details'] = pipeline_detail_list

        configurations = configuration_svc.get_all_versions_by_file_name(
            header_data.prep_method)
        configurations = [config.as_dict() for config in configurations]
        response_dict['pipeline_configuration'] = configurations

    return response_dict


def get_current_cna_details(sample_id, analysis_id):
    try:
        query = Analysis.query \
            .with_entities(Analysis.id,
                           AnalysisToolsDetails.current_detail.label(
                               'current_detail'), \
                           Request.sample_prep_methods.label('prep_method')
                           ) \
            .outerjoin(AnalysisToolsDetails) \
            .outerjoin(AnalysisTools) \
            .outerjoin(Request.samples) \
            .outerjoin(MapAnalysis) \
            .outerjoin(Map) \
            .filter(Analysis.id == analysis_id) \
            .filter(Analysis.sample_id == Sample.id) \
            .filter(AnalysisToolsDetails.analysis_id == Analysis.id) \
            .filter(AnalysisTools.name == 'CopyNumberAnalysis') \
            .filter(AnalysisTools.id == AnalysisToolsDetails.tool_id) \
            .filter(MapAnalysis.analysis_id == Analysis.id) \
            .filter(Map.id == MapAnalysis.map_id) \
            .group_by(AnalysisToolsDetails.id)
        result = query.all()
    except Exception as e:
        logger.error('Failed to get current CNA details with error: {}'
                     .format(str(e)))
        raise Exception('Failed to get current CNA details with error: ', e)

    return result


def check_duplicate_variation(position, type, gt, ref_base, total_read_depth,
                              sample_base, read_depth, purity,
                              feature_type, annotation, effects, translation,
                              organism, tier_label, map_analysis_id):
    is_duplicate = False
    try:
        duplicate_variation = Variation.query \
            .with_entities(Variation.id) \
            .filter(Variation.position == position) \
            .filter(Variation.type == type) \
            .filter(Variation.gt == gt) \
            .filter(Variation.ref_base == ref_base) \
            .filter(Variation.total_read_depth == total_read_depth) \
            .filter(Variation.sample_base == sample_base) \
            .filter(Variation.read_depth == read_depth) \
            .filter(Variation.purity == purity) \
            .filter(Variation.feature_type == feature_type) \
            .filter(Variation.annotation == annotation) \
            .filter(Variation.effects == effects) \
            .filter(Variation.translation == translation) \
            .filter(Variation.organism == organism) \
            .filter(Variation.tier_label == tier_label) \
            .filter(Variation.map_analysis_id == map_analysis_id) \
            .all()
    except Exception as e:
        logger.error('An error occurred in get duplicate variation query : {}'
                     .format(str(e)))
        raise Exception('Failed to get duplicate variation as error in query: ',
                        e)

    if duplicate_variation:
        is_duplicate = True
        return is_duplicate
    else:
        return is_duplicate


def update_analysis_tool_details(params):
    tool_details = AnalysisToolsDetails.query \
        .filter_by(analysis_id=int(params['analysis_id'])) \
        .filter_by(tool_id=int(params['tool_id'])) \
        .one_or_none()
    if tool_details:
        # only update Current Analysis Tool Details record
        tool_details.analysis_id = params.get('analysis_id',
                                              tool_details.analysis_id)
        tool_details.tool_id = params.get('tool_id', tool_details.tool_id)
        tool_details.current_call = params.get('call',
                                               tool_details.current_call)
        tool_details.current_msg = params.get('message',
                                              tool_details.current_msg)
        tool_details.current_detail = params.get('cna_detail',
                                                 tool_details.current_detail)
        db_util.db_commit()
        logger.info("Analysis Tools Details record updated successfully.")
        return tool_details
    return None
