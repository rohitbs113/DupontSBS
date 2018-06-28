from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
import os
import re
import tempfile
import logging
import boto3

import sbs.config as cfg
from sbs.utility import log_level
from sbs import app

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

conn_params = ['mysql+pymysql://',
               cfg.db_username, ':',
               cfg.db_password, '@',
               cfg.db_endpoint, '/',
               cfg.db_name]
conn_str = ''.join(conn_params)

app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
db = SQLAlchemy(app, session_options={"expire_on_commit": False})


def create_app():
    # AWS RDS MySQL
    conn_params = ['mysql+pymysql://',
                   cfg.db_username, ':',
                   cfg.db_password, '@',
                   cfg.db_endpoint, '/',
                   cfg.db_name]
    conn_str = ''.join(conn_params)

    app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = \
        cfg.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = cfg.SQLALCHEMY_ECHO
    db.init_app(app)


def init_mysql_db():
    """
    Get access to mysql db and create tables using models
    """
    try:
        import sbs.models.models
        db.create_all()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    return jsonify({"status": "success"})


def db_add_query(query):
    db.session.add(query)


def db_commit():
    db.session.commit()
    db.session.close()


def bulk_insert_mappings(mapper, mappings, return_defaults=False,
                         render_nulls=False):
    session = Session(bind=db.engine)
    session.bulk_insert_mappings(mapper, mappings, return_defaults,
                                 render_nulls)
    session.commit()
    session.close()


def bulk_update_mappings(mapper, mappings):
    session = Session(bind=db.engine)
    session.bulk_update_mappings(mapper, mappings)
    session.commit()
    session.close()



def parse_template_config(data):
    data = data.replace("\n", "@")
    regex = re.search('(.*)\[GENERAL\](.*)\[CopyNumberAnalysis\](.*)\[DistalMappingTarget\](.*)',data, re.IGNORECASE)
    general,other = ('', '')
    if regex:
        general, _, other = regex.group(2), regex.group(3), regex.group(4)
        general = general.replace("@", "\n").replace("\\n","\n").lstrip("\n")
        other = other.replace("@", "\n").replace("\\n","\n").lstrip("\n")

    return general, other


def get_current_cna_detail(sample_id, analysis_id):
    #gets current CNA(CopyNumberAnalysis) detail
    from sbs.service import analysis_service as analysis_svc
    import sbs.service.pipeline_configuration_service as configuration_svc
    #tool_detail = analysis_svc.get_call_details(analysis_id)
    tool_detail = analysis_svc.get_current_cna_details(sample_id, analysis_id)
    current_detail, template_config = ('', '')
    if tool_detail:
        current_detail = tool_detail[0].current_detail
        prep_method = tool_detail[0].prep_method
        #Gets latest pipeline configuration from DB
        config = configuration_svc.get_latest_configuration(prep_method)
        if config:
            logger.info("Found pipeline configuration data from DB")
            template_config = config.as_dict()['conf_file']

    return current_detail, template_config


def get_latest_variations(sample_id, analysis_id, observed_map_id=None):
    # Gets latest variations records from database
    from sbs.service import variation_service as var_svc
    variation_response_dict = {}
    variation_list = []
    if observed_map_id:
        variation_response = var_svc.get_integrities(analysis_id, observed_map_id)
        obs_map_id = ''
        if variation_response:
            for row in variation_response:
                row.sample_id = sample_id
                row.lab_name = row.construct_id
                obs_map_id = row.construct_id
                variation_list.append(row.as_dict())
            variation_response_dict[obs_map_id] = variation_list
    else:    
        primary_construct, _, _ = get_construct_list(sample_id, analysis_id)
        variation_response = var_svc.get_variation_by_construct(analysis_id, primary_construct)
        if variation_response:
            for row in variation_response:
                raw_variation = row[1]
                raw_variation.sample_id = sample_id
                raw_variation.lab_name = primary_construct
                variation_list.append(raw_variation.as_dict())
            variation_response_dict[primary_construct] = variation_list

    return variation_response_dict


def get_construct_list(sample_id, analysis_id):
    # Gets all constructs for sample/analysis
    from sbs.service import sample_service as sample_svc
    construct_result = sample_svc.get_primary_secondary_construct_list(sample_id, analysis_id)
    construct_list = []
    primary_map_name = ''
    if 'construct_name' in construct_result['primary_map']:
        primary_map_name = construct_result['primary_map']['construct_name']
    secondary_maps = construct_result['secondary_maps']
    construct_list.append(primary_map_name)
    for map_obj in secondary_maps:
        construct_list.append(map_obj['construct_name'])
    construct_list =[construct for construct in construct_list if construct] 

    return primary_map_name, secondary_maps, construct_list 


def get_latest_junctions(sample_id, analysis_id):
    # Gets latest junction records from database
    from sbs.service import sample_service as sample_svc
    _, _ ,construct_list = get_construct_list(sample_id, analysis_id)
    junction_response_dict = {}
    for construct in construct_list:
        junction_response = sample_svc.get_all_junctions(analysis_id, construct)

        junction_list = []

        if junction_response:
            for junction in junction_response:
                raw_junction = junction[1]
                if raw_junction:
                    # setting masked value from MAP_ANALYSIS_JUNCTION
                    raw_junction.masked = junction.masked

                    junction_list.append(raw_junction.as_dict())
            junction_response_dict[construct] = junction_list

    return junction_response_dict


def upload_files_to_s3(source_file, bucket, dest_file):
    # upload file to s3
    s3_client = boto3.client('s3', region_name=cfg.aws_region)
    s3_client.upload_file(source_file, bucket, dest_file)
    logger.info("Successfully uploaded file {} to s3".format(source_file))
    # remove temporary file
    os.remove(source_file)


junction_file_headers = ['#Masked','End','Junction_Pos','Proximal_Mapping','Distal_Mapping','Junction_Seq', \
                         'Proximal_Seq','Proximal_Len','Distal_Seq','Distal_Len','Element','Uniq_Reads', \
                         'Supporting_Reads','Source','Endogenous','Duplicates']

def upload_junction_records(sample_id, s3_output_dir, data):
    # write updated junction db records to files and upload to s3
    temp_dir = tempfile.gettempdir()
    try:
        for construct, junction_list in data.items():
            file_path = "{}/{}.{}.junctions.txt".format(temp_dir, sample_id, construct)
            junction_row_str = ""
            hdr = "\t".join(junction_file_headers)
            junction_row_str += hdr + "\n"
            with open(file_path, "w") as outfile:
                for junction in junction_list:
                    junction_row = [junction['masked'], junction['end'], junction['position'], \
                                        junction['proximal_mapping'], junction['distal_mapping'], \
                                        junction['junction_sequence'], junction['proximal_sequence'], \
                                        junction['proximal_sequence_length'], junction['distal_sequence'], \
                                        junction['distal_sequence_length'], junction['element'], \
                                        junction['unique_reads'], junction['supporting_reads'], \
                                        junction['source'], junction['endogenous'], junction['duplicates'] ]
                    junction_row = [str(x) if x else '' for x in junction_row]
                    junction_row_str += '\t'.join(junction_row) + "\n"

                # write junction rows to file
                junction_row_str = junction_row_str.rstrip("\n")
                outfile.write(junction_row_str + "\n")

            # upload junction files to s3 
            dest_file = os.path.join(s3_output_dir, os.path.basename(file_path)) 
            upload_files_to_s3(file_path, cfg.s3_bucket, dest_file)
    except Exception as e:
        logger.error('Failed to upload junction file with error: {}'
                     .format(str(e)))
        raise Exception('Failed to upload junction file with error: ', e)


variation_file_headers = ['#Sample_ID','Lab_Name','Position','Type','GT','Ref_Base','Total_Read_Depth', \
                          'Alt_Base','Alt_Read_Depth','Alt_Frequency','Feature_Type','Feature_Label', \
                          'Effects','Translation','Organism','Tier_Label']

def upload_variation_records(sample_id, s3_analysis_dir, data, new_map_id=None):
    # write updated variation db records to files and upload to s3
    temp_dir = tempfile.gettempdir()
    s3_upload_dir = os.path.join(s3_analysis_dir, cfg.analysis_read_dir_expected)
    if new_map_id:
        s3_upload_dir = os.path.join(s3_analysis_dir, cfg.analysis_read_dir_observed)
    try:
        if data and data.keys():
            primary_map = list(data.keys())[0]
            variation_list = data[primary_map]
            file_path = "{}/{}.{}.integrity.report.txt".format(temp_dir, sample_id, primary_map)
            variation_row_str = ""
            hdr = "\t".join(variation_file_headers)
            variation_row_str += hdr + "\n"
            with open(file_path, "w") as outfile:
                for variation in variation_list:
                    variation_row = [variation['sample_id'], variation['lab_name'], \
                                    variation['position'], variation['type'], variation['gt'], \
                                    variation['ref_base'], variation['total_read_depth'], \
                                    variation['sample_base'], variation['read_depth'], \
                                    variation['purity'], variation['feature_type'], \
                                    variation['annotation'], variation['effects'], variation['translation'], \
                                    variation['organism'], variation['tier_label']]
                    variation_row = [str(x) if x else '' for x in variation_row]
                    variation_row_str += '\t'.join(variation_row) + "\n"
                
                # write variation rows to file
                variation_row_str = variation_row_str.rstrip("\n")        
                outfile.write(variation_row_str + "\n")

            # Upload variation file to s3
            dest_file = os.path.join(s3_upload_dir, os.path.basename(file_path))
            upload_files_to_s3(file_path, cfg.s3_bucket, dest_file)
    except Exception as e:
        logger.error('Failed to upload integrity report file with error: {}'
                     .format(str(e)))
        raise Exception('Failed to upload integrity report file with error: ', e)


def upload_config_records(sample_id, s3_output_dir, current_detail, template_config):
    # write updated current CNA detail and other config details to file and upload to s3
    temp_dir = tempfile.gettempdir()
    try:
        local_config_file, dest_file_path, config_file = ('', '', '')
        config_file = 'config.txt'
        general, other =  parse_template_config(template_config)
        local_config_file = os.path.join(temp_dir, config_file)
        with open(local_config_file, "w") as outfile:
            outfile.write('[GENERAL]\n' + general)
            outfile.write('[CopyNumberAnalysis]\n' + current_detail +"\n")
            outfile.write('[DistalMappingTarget]\n' + other)
        dest_file_path = os.path.join(s3_output_dir, config_file) 
        upload_files_to_s3(local_config_file, cfg.s3_bucket, dest_file_path)
    except Exception as e:
        logger.error('Failed to upload config file with error: {}'
                     .format(str(e)))
        raise Exception('Failed to upload config file with error: ', e)


def upload_latest_db_records(file_type, sample_id, analysis_id, new_map_id=None):
    s3_samples_path = cfg.s3_samples_key
    #Get request id
    request_id = sample_id[:5]
    s3_analysis_dir = os.path.join(s3_samples_path, request_id, sample_id, str(analysis_id))
    s3_output_dir = os.path.join(s3_analysis_dir, cfg.analysis_read_dir_expected)
    if file_type == 'junction':
        #Get all junctions and upload
        junction_response = get_latest_junctions(sample_id, analysis_id)
        upload_junction_records(sample_id, s3_output_dir, junction_response)
    if file_type == 'variation':
        #Gets all variations and upload
        variation_response = get_latest_variations(sample_id, analysis_id, new_map_id) 
        upload_variation_records(sample_id, s3_analysis_dir, variation_response, new_map_id)
    if file_type == 'config':
        #Gets config data and upload
        current_detail, template_config= get_current_cna_detail(sample_id, analysis_id)
        upload_config_records(sample_id, s3_output_dir, current_detail, template_config) 

create_app()
