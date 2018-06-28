import datetime
import logging

from sqlalchemy import func
from sqlalchemy import or_

import sbs.database_utility as db_util
from sbs.models.Analysis import Analysis
from sbs.models.Analysis import RequestType
from sbs.models.Crop import Crop
from sbs.models.Error import Error
from sbs.models.Map import Map
from sbs.models.MapAnalysis import MapAnalysis
from sbs.models.ObservedMap import ObservedMap
from sbs.models.Request import Request
from sbs.models.RequestComment import RequestComment
from sbs.models.Sample import Sample
from sbs.models.TxMethod import TxMethod
from sbs.models.Variation import Variation
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def get_request_by_request_id(request_id):
    return fetch_requests(request_id)


def get_requests(role='client'):
    return fetch_requests(None, role)


def fetch_requests(request_id=None, role='client'):
    """"
    Provides SbS request records
    """
    results = None
    try:
        query = Request.query \
            .with_entities(Request,
                           Analysis.id.label("analysis_id"),
                           func.group_concat(func.CONCAT_WS
                                             (';', Sample.curr_alpha_analysis,
                                              Analysis.id, Analysis.type)
                                             .distinct()).label("analysis_type"),
                           func.group_concat(func.CONCAT_WS
                                             (';', Analysis.id, Analysis.load_date)
                                             .distinct()).label("load_date"),
                           Crop.organism.label("organism"),
                           TxMethod.method_name.label("tx_method"),
                           func.count(RequestComment.id.distinct()).label('total_comments'),
                           func.count(Error.id.distinct()).label('total_errors'),
                           func.count(Sample.id.distinct()).label('total_samples')
                           ) \
            .outerjoin(Sample) \
            .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
            .outerjoin(Crop) \
            .outerjoin(TxMethod) \
            .outerjoin(RequestComment) \
            .outerjoin(Error) \
            .group_by(Request.id)

        if request_id:
            query = query.filter(request_id == Request.id)
            results = query.one_or_none()
        else:
            results = query.all()

    except Exception as e:
        logger.error('An error occurred in get request query : {}'
                     .format(str(e)))
        raise Exception('Failed to get request as error in query: ', e)
    requests_list = []
    total_requests = 0

    if results:

        if request_id:
            total_requests = 1
            if role and role == "client":
                requests_list.append(get_request(results).browse_request_client_as_dict())
            else:
                requests_list.append(get_request(results).browse_request_as_dict())
        else:
            total_requests = len(results)

            for result in results:
                if role and role == "client":
                    requests_list.append(get_request(result).browse_request_client_as_dict())
                else:
                    requests_list.append(get_request(result).browse_request_as_dict())

        requests_list = sorted(requests_list, key=lambda x: x['load_date'],
                               reverse=True)

    for obj in requests_list:
        load_date = obj['load_date'].split(" ")[0]
        obj['load_date'] = load_date
    requests = {'requests': requests_list, 'total_requests': total_requests}
    logger.info('total request is :[{}]'.format(total_requests))

    return requests


def get_request(results):
    """
    Sets all required request attributes and returns request's object
    """
    request = results[0]

    if request:
        request.tx_method = results.tx_method

        if results.analysis_type:
            alpha_count, delta_count = get_alpha_delta_count(results.
                                                             analysis_type.
                                                             split(','))
            request.alpha_samples = alpha_count
            request.delta_samples = delta_count

        request.organism = results.organism

        if results.load_date:
            sbs_load_dates = get_values(results.load_date.split(','))
            sbs_load_date = get_latest_load_date(sbs_load_dates)
            request.load_date = sbs_load_date

        request.total_comments = results.total_comments
        request.total_errors = results.total_errors
        request.total_samples = results.total_samples
    return request


def get_alpha_delta_count(values):
    """
    Returns alpha and delta count for a request
    """
    alpha_count, delta_count = (0, 0)

    for x in values:
        value = x.split(';')

        if len(value) > 2:
            curr_alpha_analysis = value[0]
            analysis_id = value[1]
            analysis_type = value[2]

            if analysis_id == curr_alpha_analysis:
                alpha_count += 1

            elif analysis_id != curr_alpha_analysis \
                    and RequestType[analysis_type] == RequestType.delta:
                delta_count += 1
        elif len(value) > 1:
            analysis_type = value[1]
            if RequestType[analysis_type] == RequestType.delta:
                delta_count += 1

    return alpha_count, delta_count


def get_values(values):
    """
    Returns required list of values by separating a string by delimiters
    """
    values_list = []

    for x in values:
        value = x.split(';')

        if len(value) > 1:
            values_list.append(value[1])
    return values_list


def get_latest_load_date(load_date):
    """
    Gets latest sbs_load_date
    """
    try:
        latest_load_date = ""

        if load_date:
            load_date_list = map(lambda x: datetime.datetime.
                                 strptime(x, '%Y-%m-%d %H:%M:%S'), load_date)
            latest_load_date = str(max(load_date_list))
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to get latest load date: ', e)
    return latest_load_date


def update_request(params):
    """
    Update Request Info
    """
    request_primary_id = None

    try:
        request_object = get_request_object(params['request_id'])
        request_primary_id = request_object.id

        if not request_primary_id:
            raise Exception("Failed to update Request {}: Request does not "
                            "exists".format(params['request_id']))

        request = Request.query.get(request_primary_id)
        request.request_id = params.get('request_id', request.request_id)
        request.sample_prep_methods = params.get('sample_prep_methods',
                                                 request.sample_prep_methods)
        request.sbs_internalpipeline_version = params.get('sbs_internalpipeline_version',
                                                          request.sbs_internalpipeline_version)
        request.request_name = params.get('request_name', request.request_name)
        request.released_on = params.get('released_on', request.released_on)
        request.sbs_status = params.get('sbs_status', request.sbs_status)
        request.organism_id = params.get('organism_id', request.organism_id)

        if 'tx_method' in params and params['tx_method']:
            try:
                tx_method = TxMethod.query \
                    .filter_by(method_name=params['tx_method']) \
                    .first()
            except Exception as e:
                logger.error('Failed to get tx_method with error: {}'
                             .format(str(e)))
                raise Exception('Failed to get tx_method with error: ', e)
            if tx_method:
                request.tx_method_id = tx_method.id

        db_util.db_commit()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update Request with error: ', e)

    if request:
        logger.info("Successfully updated Request for request_id [{}]."
                    .format(params['request_id']))

        return get_request_by_request_id(request_primary_id)
    else:
        return {"status": "Failed to update sbs_status/transformation method "
                          "for id {}.".format(params['request_id'])}


def delete_request(request_id):
    """
    Deletes request record
    """
    try:
        request = Request.query \
            .filter_by(request_id=request_id) \
            .delete()
        db_util.db_commit()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to delete request with error: ', e)

    if request:
        return {"status": "Deleted request for Request id [{}]".format(request_id)}
    else:
        return {"status": "Error while deleting Request id [{}]".format(request_id)}


def add_request(params):
    """
    Adds request record or raise exception if already exists
    """
    request = None
    try:
        request_id = params['request_id'].rstrip('/')
        request = Request.query.filter_by(request_id=request_id).one_or_none()
        if request:
            logger.info("Request with request id [{}] already exists." \
                        .format(params['request_id']))
            return request

        sample_prep_methods = params.get('sample_prep_methods', None)
        sbs_internalpipeline_version = params.get('sbs_internalpipeline_version', None)
        request_name = params.get('request_name', None)
        released_on = params.get('released_on', None)
        sbs_status = params.get('sbs_status', None)
        researcher = params.get('researcher', None)
        tx_method_id = params.get('tx_method_id', None)
        organism_id = params.get('organism_id', None)

        request = Request(request_id,
                          sample_prep_methods,
                          sbs_internalpipeline_version,
                          request_name,
                          released_on,
                          sbs_status,
                          tx_method_id,
                          researcher,
                          organism_id)
        db_util.db_add_query(request)
        db_util.db_commit()
        logger.info("Request record for request id [{}] added successfully."
                    .format(params['request_id']))
        request = Request.query.filter_by(request_id=request_id).one_or_none()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to add Request with error: ', e)

    return request


def set_sample_records(result, sample, analysis):
    sample.current_call = analysis.current_call
    sample.pipeline_call = analysis.pipeline_call
    sample.status = analysis.sbs_status
    sample.load_date = analysis.load_date
    sample.is_visible = analysis.is_visible_to_client
    sample.type = analysis.type
    sample.analysis_id = analysis.id
    sample.observed_map_id = result.observed_map_id
    tier_label_list = get_values(result.variations.split(','))
    sample.total_variations = get_variation_count(tier_label_list)
    sample.total_errors = result.total_errors
    sample.single_read_count = analysis.single_read_count
    sample.paired_read_count = analysis.paired_read_count
    sample.complete_probe_coverage = analysis.complete_probe_coverage
    sample.target_rate = analysis.target_rate
    sample.tier_3_reason = analysis.tier_3_reason
    sample.sbs_version = analysis.sbs_version
    sample.reference = analysis.reference
    sample.call_comment = analysis.call_comment
    sample.manual_set = analysis.manual_set
    maps = get_values(result.total_maps.split(','))
    sample.total_maps, sample.total_pending_maps = get_maps_count\
        (maps)
    sample.configuration_id = analysis.configuration_id


def get_sample_query_filters(params, query):
    if 'request_id' in params and params['request_id']:
        query = query.filter(Sample.request_id == params['request_id'])
    if 'sample_id' in params and params['sample_id']:
        query = query.filter(Sample.id == params['sample_id'])
    if 'analysis_id' in params and params['analysis_id']:
        query = query.filter(Analysis.id == params['analysis_id'])
    if 'filter_type' in params and params['filter_type']:
        if params['filter_type'] == 'alpha':
            query = query.filter(or_(Analysis.type == 'alpha', Analysis.type == 'alphad'))
        elif params['filter_type'] == 'delta':
            query = query.filter(Analysis.type == 'delta')
    return query


def get_samples_query():
    query = Sample.query \
        .with_entities(Sample,
                       Analysis,
                       func.group_concat(func.CONCAT_WS
                                         (';', Variation.id, Variation.tier_label)
                                         .distinct()).label("variations"),
                       ObservedMap.id.label('observed_map_id'),
                       func.count(Error.id.distinct()).label('total_errors'),
                       func.group_concat(func.CONCAT_WS
                                         (';', Map.id, Map.construct_id)
                                         .distinct()).label("map"),
                       func.group_concat(func.CONCAT_WS
                                         (';', ObservedMap.id, ObservedMap.status)
                                         .distinct()).label("total_maps")
                       ) \
        .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
        .outerjoin(MapAnalysis) \
        .outerjoin(Map) \
        .outerjoin(ObservedMap) \
        .outerjoin(Error) \
        .outerjoin(Variation) \
        .group_by(Analysis.id)

    return query


def get_request_object(request_id):
    result = Request.query \
        .with_entities(Request) \
        .filter_by(request_id=request_id) \
        .one_or_none()

    if result:
        return result


def get_samples(request_id, role='client', filter_type=None):
    """
    Provides all samples for particular request_id
    """
    results = None
    params = {}
    request_primary_id = None
    try:
        request_object = get_request_object(request_id)

        if request_object:
            request_primary_id = request_object.id

        if request_primary_id:
            params['request_id'] = request_primary_id
            if filter_type:
                params['filter_type'] = filter_type
            query = get_sample_query_filters(params, get_samples_query())

            if role and role == 'client':
                query = query.filter(Analysis.is_visible_to_client)

            results = query \
                .order_by(Sample.id) \
                .all()
    except Exception as e:
        logger.error('An error occurred in get all samples query : {}'
                     .format(str(e)))
        raise Exception('Failed to get Samples as error in query: ', e)

    result_list = []
    total_request_errors = 0
    constructs = {'primary_map': '', 'secondary_maps': ''}
    if results:

        for result in results:
            sample = result[0]
            analysis = result[1]

            if sample and analysis:

                if role and role == 'client':
                    constructs['primary_map'] = sample.construct_name

                    if result.map:
                        secondary_maps = get_values(result.map.split(','))

                        if sample.construct_name in secondary_maps:
                            secondary_maps.remove(sample.construct_name)

                        constructs['secondary_maps'] = secondary_maps
                    sample.construct_ids = constructs
                set_sample_records(result, sample, analysis)
                total_request_errors += result.total_errors

                if sample.curr_alpha_analysis == analysis.id \
                        or analysis.type == RequestType.delta:
                    result_list.append(sample.browse_sample_as_dict())

    if role and role == 'client':
        if result_list:
            for result in result_list:
                if result['current_call'] == 'Tier 1':
                    result['current_call'] = 'GREEN'
                elif result['current_call'] == 'Tier 2':
                    result['current_call'] = 'YELLOW'
                elif result['current_call'] == 'Tier 3':
                    result['current_call'] = 'RED'

    total_samples = len(result_list)
    samples = {'result': result_list, 'total_samples': total_samples,
               'total_request_errors': total_request_errors}

    return samples


def get_maps_count(maps):
    total_maps = 0
    total_pending_maps = 0

    for map in maps:
        if map.lower() == 'pending':
            total_pending_maps += 1
        else:
            total_maps += 1

    return total_maps, total_pending_maps


def get_variation_count(tier_label_list):
    """
    Returns total variations count for tier_label with 'update_map' value
    """
    total_variations = 0

    for tier_label in tier_label_list:

        if tier_label.lower() == 'update_map':
            total_variations += 1

    return total_variations


def get_request_comments(request_id):
    """
    Returns list of all comments for particular request id
    """
    results = None

    try:
        results = Request.query \
            .with_entities(Request.id, RequestComment) \
            .outerjoin(RequestComment) \
            .filter(Request.request_id == request_id) \
            .order_by(RequestComment.created_on.desc()) \
            .all()
    except Exception as e:
        logger.error('An error occurred: {}'
                     .format(str(e)))
        raise Exception('Failed to get comments as error in query: ', e)

    result_list = []

    if results:

        for result in results:
            request_comment = result[1]

            if request_comment:
                result_list.append(request_comment.as_dict())

    return result_list


def add_request_comments(request_id, params):
    """
    Adds Comment for particular request
    """
    request_primary_id = None

    try:
        request_object = get_request_object(request_id)
        if request_object:
            request_primary_id = request_object.id

        if request_primary_id:
            request_comment = RequestComment(params['comment'],
                                             request_primary_id,
                                             params['username'],
                                             params['username'])
            db_util.db_add_query(request_comment)
            db_util.db_commit()
            logger.info("Comment record for request id [{}] added successfully."
                        .format(request_id))

            return "Successfully added comment for request {}".format(request_id)

        else:
            raise Exception("Failed to add comment for request {}".format(request_id))

    except Exception as e:
        logger.error('An error occurred : {}'
                     .format(str(e)))
        raise Exception('Failed to add Comments for Request as error in query: ', e)


def get_map_analysis_by_request(request_id):
    try:
        result = Request.query \
            .with_entities(MapAnalysis.id.label("map_analysis_id")) \
            .outerjoin(Request.samples) \
            .outerjoin((Analysis, Sample.id == Analysis.sample_id)) \
            .outerjoin(MapAnalysis, Analysis.id == MapAnalysis.analysis_id) \
            .filter(Request.request_id == request_id).all()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to fetch map analysis ids for request: ', e)

    return result


def submit_request(params):
    """
    Adds Request, Sample and Analysis records
    """
    sample_list = []

    try:
        request_result = add_request(params)
        params['request_id'] = request_result.id
        result = {"request_id": request_result.request_id}

        for sample in params['samples']:
            sample_analysis_dict = {}
            import sbs.service.sample_service as sample_svc
            import sbs.service.analysis_service as analysis_svc
            params['sample_id'] = sample
            sample_result = sample_svc.add_sample(params)
            sample_analysis_dict['sample_id'] = sample_result.sample_id
            analysis_result = analysis_svc.add_analysis(params)
            sample_analysis_dict['analysis_id'] = analysis_result.id
            sample_list.append(sample_analysis_dict)

        result['samples'] = sample_list
    except Exception as e:
        logger.error('An error occurred while submitting request : {}'
                     .format(str(e)))
        raise Exception('Failed to submit request with error {}'.format(e))

    return result


def get_sample_by_request_id(params):
    request_primary_id = None
    fetch_only_first = params['fetch_only_first']
    results = None
    try:
        # get individual sample/analysis record
        request_object = get_request_object(params['request_id'])

        if request_object:
            request_primary_id = request_object.id
        if request_primary_id:
            params['request_id'] = request_primary_id
            query = get_sample_query_filters(params, get_samples_query())
            results = query.order_by(Sample.id).all()
    except Exception as e:
        logger.error('An error occurred in getting sample info query : {}'
                     .format(str(e)))
        raise Exception('Failed to get Sample info as error in query: ', e)
    result_list = []
    if results:

        for result in results:
            sample = result[0]
            analysis = result[1]

            if sample and analysis:
                if sample.curr_alpha_analysis == analysis.id \
                        or analysis.type == RequestType.delta:
                    result_list.append(result)

    if fetch_only_first:
        results = []
        if result_list:
            results.append(result_list[0])
            return results

    return results
