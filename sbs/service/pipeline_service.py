import hashlib
import logging
import time

import boto3

import sbs.config as cfg
import sbs.database_utility as db_util
from sbs.models.Analysis import Analysis
from sbs.utility import log_level

TIMEOUT = 'TIMEOUT'

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def submit_proj_level_dup_detection_pipeline_job(request_id, sample_id,
                                                 analysis_id, outfilename):
    job_name = 'proj_level_dup_det-{}-{}-{}'.format(str(sample_id),
                                                    str(analysis_id),
                                                    date_hash())
    job_queue_name = cfg.main_queue
    job_definition = cfg.dd_jobdef_name

    script = 'sbs-pipeline/bin/EC2_DuplicationDetection.sh'
    command = ["sh",
               script,
               str(request_id),
               str(sample_id),
               str(analysis_id),
               str(outfilename),
               "--bucket", cfg.s3_bucket
               ]

    response = submit_job(command, job_name, job_queue_name, job_definition)

    return response


def submit_gene_disruption_pipeline_job(request_id, sample_id, analysis_id,
                                        map_id, organism, nthread):
    job_name = 'gene-disruption-{}-{}-{}'.format(str(sample_id),
                                                 str(analysis_id), date_hash())
    job_queue_name = cfg.quick_queue
    job_definition = cfg.gd_jobdef_name

    s3_output_path = 's3://{}/sbs-data/Samples/{}/{}/{}/output' \
        .format(cfg.s3_bucket, request_id, sample_id, analysis_id)
    s3_junction_file = '{}/{}.{}.junctions.txt' \
        .format(s3_output_path, sample_id, map_id)

    script = 'sbs-pipeline/bin/EC2_GeneDisruption.sh'
    command = ["sh",
               script,
               s3_junction_file,
               s3_output_path,
               "--bucket", cfg.s3_bucket
               ]
    if organism:
        command.append("-o", organism)
    if nthread:
        command.append("-t", nthread)

    response = submit_job(command, job_name, job_queue_name, job_definition)

    return response


def submit_junction_ext_pipeline_job(sample_id, junction_seq, junction_end,
                                     analysis_id, map_id):
    job_name = 'junction-ext-{}-{}-{}'.format(str(sample_id),
                                              str(analysis_id), date_hash())
    job_queue_name = cfg.quick_queue
    job_definition = cfg.je_jobdef_name

    script = 'sbs-pipeline/bin/EC2_JunctionExtension.sh'
    command = ["sh",
               script,
               str(junction_seq),
               str(junction_end),
               str(sample_id),
               str(map_id),
               str(analysis_id),
               "--bucket", cfg.s3_bucket
               ]

    response = submit_job(command, job_name, job_queue_name, job_definition)

    return response


def submit_wildtype_pipeline_job(sample_id, analysis_id, map_id):
    job_name = 'endogenous-pipeline-{}-{}-{}'.format(str(sample_id),
                                                     str(analysis_id),
                                                     date_hash())
    job_queue_name = cfg.main_queue
    job_definition = cfg.wt_jobdef_name

    script = 'sbs-pipeline/bin/EC2_EndogenousPipeline.sh'
    command = ["sh",
               script,
               str(sample_id),
               str(analysis_id),
               str(map_id),
               "--bucket", cfg.s3_bucket
               ]

    response = submit_job(command, job_name, job_queue_name, job_definition)

    return response


def submit_routine_pipeline_job(request_id, sample_id, analysis_id):
    """
     Adds analysis for given sample id and creates a S3 folder for analysis id
     in which pipeline results will be published and then submits the routine
     pipeline to aws batch job
    """
    job_queue_name = cfg.main_queue
    job_definition = cfg.rt_jobdef_name
    script = 'sbs-pipeline/bin/EC2_RoutinePipeline.sh'
    command = ["sh",
               script,
               str(sample_id),
               str(analysis_id),
               "--bucket", cfg.s3_bucket]

    job_name = 'routine-pipeline-{}-{}-{}'.format(str(sample_id),
                                                  str(analysis_id), date_hash())
    response = submit_job(command, job_name, job_queue_name, job_definition)

    return response


def date_hash():
    """
    Creates Date hash value
    """
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))

    return hash.hexdigest()


def submit_job(command, job_name, job_queue, job_def):
    """
    Submit pipeline Job as AWS Batch Job
    """
    logger.info('Submitting pipeline job: {}'.format(job_name))
    client = boto3.client('batch', region_name=cfg.aws_region)
    response = client.submit_job(jobName=job_name,
                                 jobQueue=job_queue,
                                 jobDefinition=job_def,
                                 containerOverrides={
                                     'command': command
                                 })

    return response


def submit_recalculate_pipeline_call_job(sample_id, analysis_id, waiting_time):
    try:
        analysis = Analysis.query.filter_by(id=analysis_id).one()

        if not analysis:
            raise Exception("Failed to get Analysis record")

        analysis.manual_set = None
        analysis.current_call = "Pending"
        db_util.db_commit()
        logger.info("Analysis record for manual_set column updated "
                    "successfully.")
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update manual_set column of Analysis '
                        'with error: ', e)

    # Get latest DB records and upload to s3
    db_util.upload_latest_db_records('junction', sample_id, analysis_id)
    db_util.upload_latest_db_records('variation', sample_id, analysis_id)
    db_util.upload_latest_db_records('config', sample_id, analysis_id)

    # submit batch job
    job_name = 'recalculate-call-{}-{}-{}' \
        .format(str(sample_id), str(analysis_id), date_hash())
    job_queue_name = cfg.recal_queue
    job_definition = cfg.rt_jobdef_name

    script = 'sbs-pipeline/bin/EC2_RecalculatePipeline.sh'
    command = ["sh",
               script,
               str(sample_id),
               str(analysis_id),
               "--bucket", cfg.s3_bucket]

    response = submit_job(command, job_name, job_queue_name, job_definition)

    job_id = response['jobId']

    if waiting_time:
        timeout = time.time() + 18  # 18 secs from now
        status = get_job_status(job_id, timeout)
    else:
        status = {"job_id": job_id,
                  "job_name": job_name,
                  "sample_id": sample_id,
                  "analysis_id": analysis_id
                  }

    if status == TIMEOUT:
        logger.info('Failed to get status for recalculate pipeline call '
                    'job id {}. Timeout occurred.'.format(job_id))
        return TIMEOUT
    else:
        logger.info('Status for Recalculate pipeline call job {} is {}'
                    .format(job_name, status))
        return status


def get_batch_job_status(job_id):
    client = boto3.client('batch', region_name=cfg.aws_region)
    response = client.describe_jobs(
        jobs=[job_id, ],
    )
    status = response['jobs'][0]['status']

    return status


def get_job_status(job_id, timeout):
    status = get_batch_job_status(job_id)
    if status == 'SUCCEEDED' or status == 'FAILED':
        return status
    else:
        time.sleep(0.5)
        if time.time() > timeout:
            return TIMEOUT
        else:
            return get_job_status(job_id, timeout)


def submit_regenerate_observed_map_call_job(params):
    new_map_id = str(params['new_map_id'])
    map_id = new_map_id.split('.')[0]
    job_name = 'observed-map-{}-{}'.format(str(new_map_id.replace('.','-')), date_hash())
    job_queue_name = cfg.quick_queue
    job_definition = cfg.je_jobdef_name
    
    script = 'sbs-pipeline/bin/EC2_ObservedMap.sh'
    command = ["sh",
               script,
               str(params['sample_id']),
               str(params['analysis_id']),
               map_id,
               new_map_id,
               "--analysis_read_dir", params['analysis_read_dir'],
               "--bucket", cfg.s3_bucket
               ]
    if 'slices' in params and params['slices']:
        command.append("-l", str(params['slices']))

    response = submit_job(command, job_name, job_queue_name, job_definition)

    return response
