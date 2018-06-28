import logging
import re

import boto3

import sbs.config as cfg
import sbs.database_utility as db_util
from sbs.models.PipelineConfiguration import PipelineConfiguration
import sbs.service.junction_service as junc_svc
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def get_config_file_from_s3(config_filename):
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    bucket_name = cfg.s3_bucket 
    file_content = str(s3.Object(bucket_name, 'sbs-data/ini/' + config_filename).get()['Body'].read()).split("'")[1]
    logger.info("Reading file {} from s3 bucket {}".format(config_filename, bucket_name))
    return {"file_name": config_filename.split(".")[0], "file_content": file_content}


def get_endo_junction_set_name(file_content):
    file_content = file_content.replace('\n', '@')
    regex = re.search('^(.*)ENDOGENOUS_SET=(.*)FIND(.*)',file_content, re.IGNORECASE)
    set_name = ''
    if regex:
        set_name = regex.group(2).replace("\\n","\n").rstrip("\n")

    return set_name

def save_configuration(file_name, file_content):
    try:
        version = int(get_latest_version_by_name(file_name))
        version += 1
        set_name = get_endo_junction_set_name(file_content)
        pipeline_configuration = PipelineConfiguration(file_name, version, file_content, set_name)
        db_util.db.session.add(pipeline_configuration)
        db_util.db.session.commit()
        # Add endogenous set name to Endogenous table
        junc_svc.add_endo_junction_set(set_name)
    except Exception as e:
        raise Exception("Exception occurred while saving configurator data: {}".format(e))
    config_dict =  pipeline_configuration.as_dict()
    db_util.db.session.close()
    return config_dict


def get_latest_version_by_name(file_name):
    try:
        pipeline_configuration = PipelineConfiguration.query.filter_by(name=file_name) \
            .order_by(PipelineConfiguration.version.desc()).limit(1).all()
    except Exception as e:
        raise Exception("Exception occurred while fetching latest version of file {}: {}".format(file_name, e))

    if pipeline_configuration:
        return pipeline_configuration[0].version
    else:
        return 0


def get_latest_configuration(prep_method):
    try:
        pipeline_configuration = PipelineConfiguration.query \
                                 .filter_by(name=prep_method) \
                                 .order_by(PipelineConfiguration.version.desc()).limit(1) \
                                 .one_or_none()
    except Exception as e:
        logger.error("Exception occurred while fetching latest configuration {}: {}".format(prep_method, e))
        return None

    return pipeline_configuration


def list_conf_files():
    try:
        return PipelineConfiguration.query.with_entities(PipelineConfiguration.name).group_by(
            PipelineConfiguration.name).all()
    except Exception as e:
        raise Exception("Exception occurred listing pipeline configuration files: {}".format(e))


def get_conf_file_by_name_and_version(file_name, version):
    try:
        return PipelineConfiguration.query.with_entities(
            PipelineConfiguration) \
            .filter_by(name=file_name) \
            .filter_by(version=version) \
            .one_or_none()
    except Exception as e:
        raise Exception("Exception occurred fetching file {} with version {} : {}".format(file_name, version, e))


def get_all_versions_by_file_name(file_name):
    try:
        return PipelineConfiguration.query.with_entities(
                PipelineConfiguration) \
                .filter_by(name=file_name) \
                .all()
    except Exception as e:
        raise Exception("Exception occurred fetching file {} : {}".format(file_name, e))
