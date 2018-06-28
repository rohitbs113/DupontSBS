import json
import logging
import os
import tempfile

import boto3
import pyBigWig

import sbs.config as cfg
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def set_cap(number):
    caps = [100, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, \
            10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000, \
            30000, 35000, 40000, 45000, 50000, 75000, 100000]
    chosen_cap = 0
    diff = 1000000
    
    for c in caps:
        ldiff = number - c
        if (ldiff < diff) and (ldiff > 0):
            chosen_cap = c
            diff = ldiff
    
    return chosen_cap


def get_s3_presigned_url(bucket, key, expires_in):
    try:
        s3 = boto3.client('s3', region_name=cfg.aws_region)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expires_in
        )

        return url
    except Exception as e:
        raise {
        'failed to create S3 presigned url for path {}/{}'.format(bucket, key)}


def get_s3_jbrowse_data(s3_lookup_path):
    s3_client = boto3.client('s3', region_name=cfg.aws_region)
    bucket = cfg.s3_bucket
    response = s3_client.list_objects(
        Bucket=bucket,
        Prefix=s3_lookup_path
    )

    return response

msa_track_style =  {
                        "className": "feature",
                        "color" : "function(feature) { return {'omsa1':'#ffa300','omsa2':'#a1561c'}[feature.get('type')]|| '#ffa300'; }",
                        "height" : 35,
                        "showLabels": False
                }

primary_msa_menu = [
                        {
                            "label": "MSA Bowtie View",
                            "action": "{openMSAWindowBowtie}",
                            "iconClass": "dijitIconBookmark"
                        },
                        {
                            "label": "MSA Integrity View",
                            "action": "{openMSAWindowIntegrity}",
                            "iconClass": "dijitIconBookmark"
                        },
                        {
                            "label": "MSA Integrity Haplotype View",
                            "action": "{openMSAWindowHaplotype}",
                            "iconClass": "dijitIconBookmark"
                        },
                        {
                            "label": "MSA Junction View",
                            "action": "{openMSAWindowJunction}",
                            "iconClass": "dijitIconBookmark"
                        }
                ]


secondary_msa_menu = [
                        {
                            "label": "MSA Bowtie View",
                            "action": "{openMSAWindowBowtie}",
                            "iconClass": "dijitIconBookmark"
                        },
                        {
                            "label": "MSA Junction View",
                            "action": "{openMSAWindowJunction}",
                            "iconClass": "dijitIconBookmark"
                        }
                    ]


variation_menu = [
                        {
                            "label": "MSA Integrity View",
                            "action": "{MSAWindowIntegrity}",
                            "iconClass": "dijitIconBookmark"
                        }
                ]


track_order_dict = {
                    "Reference sequence": 12, "Features": 1, "Bowtie Read Coverage": 2, "Genomic Coverage Chart": 4, 
                    "Integrity Analysis Coverage": 3,
                    "Genomic Map Unique Depth": 5, "Nongenomic Map Unique Depth": 6,
                    "Genomic Map Repetitive Depth": 7, "Nongenomic Map Repetitive Depth": 8,
                    "Junctions": 9, "Variations": 10, "Open MSA": 11,
                    "Integrity Analysis - Haplotype Caller": 4
                }


def get_bam_type_json(bucket, s3_lookup_path, expires):
    response = {}
    if s3_lookup_path.endswith(".bam"):
        response['urlTemplate'] = get_s3_presigned_url(bucket, s3_lookup_path, expires)
        response['baiUrlTemplate'] = get_s3_presigned_url(bucket, s3_lookup_path+".bai", expires)

    return response

def get_bigwig_type_json(bucket, s3_lookup_path, expires):
    response = {}
    if s3_lookup_path.endswith(".bwig"):
        response['urlTemplate'] = get_s3_presigned_url(bucket, s3_lookup_path, expires)
    return response


def get_trackdata_response_json(file_path):
    data = {}
    try:
        with open(file_path) as f:
            data = json.load(f)
    except Exception as e:
        print("Error while reading expected test json file: ", e)
    
    return data


def update_track_json(bucket, track_json_file, expires):
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    api_path = "{}/sbs/jbrowse/file".format(cfg.domain_url)
    json_data ={}
    try:
        url_path = ""
         
        url_path = os.path.split(track_json_file)[0]
        query_params = api_path+"?path="+url_path+"/"
        obj = s3.Object(bucket,track_json_file)
        data = obj.get()['Body'].read().decode('utf-8')
        json_data = json.loads(data)
        url_info = json_data['histograms']['meta']
        for obj in url_info:
            if 'urlTemplate' in obj['arrayParams']:
                url = query_params+obj['arrayParams']['urlTemplate']
                obj['arrayParams']['urlTemplate'] = url
        if 'urlTemplate' in json_data['intervals']:
            url  = query_params+json_data['intervals']['urlTemplate']
            json_data['intervals']['urlTemplate'] = url
        json_data['histograms']['meta'] = url_info  
        temp_path = os.path.join(tempfile.gettempdir(), "trackData.json")
        with open(temp_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=4)
        s3_client = boto3.client('s3', region_name=cfg.aws_region)
        dest_path = os.path.join(os.path.split(track_json_file)[0],"trackData1.json")
        s3_client.upload_file(temp_path, bucket, dest_path)
        print("done uploading file...\n")
    except Exception as e:
        print("Error:", str(e))

def get_refsequence_type_json(bucket, s3_lookup_path, expires):
    response = get_s3_jbrowse_data(s3_lookup_path)
    temp_url = ""
    if 'Contents' not in response.keys():
        return temp_url
    for item in response['Contents']:
        refseq_dict = {}
        if item['Key'].endswith("refSeqs.json"):
            temp_url = get_s3_presigned_url(bucket, item['Key'], expires)
        if not refseq_dict:
            continue

    return temp_url

def get_refernce_type_txt_url(bucket, s3_lookup_path, expires):
    response = get_s3_jbrowse_data(s3_lookup_path)
    txt_template_url = ""
    for item in response['Contents']:
        if 'Contents' not in response.keys():
            return txt_template_url
        if item['Key'].endswith('.txt'):
            txt_template_url = get_s3_presigned_url(bucket, item['Key'], expires)
    
    return txt_template_url

def get_dynamic_response(fpath):
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    bucket = cfg.s3_bucket
    expires = "864000"
    json_data = {}
    obj = s3.Object(bucket,fpath)
    data = obj.get()['Body'].read().decode('utf-8')
    json_data = json.loads(data)

    return json_data


def get_php_type_json(bucket, s3_lookup_path, expires):
    response = get_s3_jbrowse_data(s3_lookup_path)
    url_temp = ""
    if 'Contents' not in response.keys():
        return url_temp
    for item in response['Contents']:
        if item['Key'].endswith("trackData.json"):
            temp_track_data = os.path.join(os.path.split(item['Key'])[0],"trackData.json")
            temp_track_data1 = os.path.join(os.path.split(item['Key'])[0],"trackData1.json")
            update_track_json(bucket, temp_track_data, expires)
            url_temp = get_s3_presigned_url(bucket,temp_track_data1, expires)
        if not url_temp:
            continue
    return url_temp


def replace_key_name(key):
    if key=='Haplotype Coverage Chart':
       key = 'Integrity Analysis - Haplotype Caller' 

    return key


def list_s3_dir(s3_dir):
    client = boto3.client('s3', region_name=cfg.aws_region)
    result = client.list_objects(Bucket=cfg.s3_bucket,
                                 Prefix=s3_dir,
                                 Delimiter='/'
                                 )
    return result


def check_available_tracks(track_dir, track_label):
    track_list = []
    track_exist = False
    result = list_s3_dir(track_dir)
    if not 'CommonPrefixes' in result.keys():
        track_list = []
    for obj in result.get('CommonPrefixes'):
        track_list.append(os.path.basename(obj.get('Prefix').rstrip('/')))
    if track_label in track_list:
        track_exist = True

    return track_exist


def check_bigwig_files(s3_bigwig_dir, bigwig_file):
    bigwig_exist = False
    response = get_s3_jbrowse_data(s3_bigwig_dir)
    if 'Contents' not in response.keys():
        bigwig_exist = False
    for item in response['Contents']:
        if bigwig_file in item['Key']:
            bigwig_exist = True
    
    return bigwig_exist


def process_json(tracklist_json, bucket, fpath, expires, map_type, construct_id):
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    reference_seq_url = ""
    for obj in tracklist_json['tracks']:
        if obj['type'] == "SequenceTrack":
            seqpath = os.path.join(fpath, "seq")
            presinged_url_template= get_refsequence_type_json(bucket, seqpath, expires)
            obj['urlTemplate'] =  presinged_url_template
            obj['txt_urlTemplate'] = get_refernce_type_txt_url(bucket, seqpath, expires)
            reference_seq_url =  obj['urlTemplate']
        if obj['type'] == "CanvasFeatures":
            track_dir = os.path.join(fpath, "tracks/")
            track_exist = check_available_tracks(track_dir, obj['label'])
            if not track_exist:
                obj['track_data'] = ''
            obj['key'] = replace_key_name(obj['key']).replace('_', ' ')
            track_path = os.path.join(fpath, "tracks", obj['label'])
            obj['urlTemplate'] = get_php_type_json(bucket,track_path, expires)
        if obj['storeClass'] == "JBrowse/Store/SeqFeature/BAM":
            bamfile = os.path.join(fpath, obj['urlTemplate'].replace("./",""))
            presigned_url  = get_bam_type_json(bucket,bamfile, expires)
            obj['urlTemplate'] = presigned_url['urlTemplate']
            obj['baiUrlTemplate'] = presigned_url['baiUrlTemplate']
        if obj['key'] == 'Open MSA':
            obj['style'] = msa_track_style
            if map_type == "primary":
                obj['menuTemplate'] = primary_msa_menu
            else:
                obj['menuTemplate'] = secondary_msa_menu
        if obj['key'] == 'Variations':
            obj['menuTemplate'] = variation_menu
            obj['category'] = 'Tracks'
        if obj['storeClass'] == "JBrowse/Store/SeqFeature/BigWig":
            obj['key'] = replace_key_name(obj['key'])
            bigwigfile = os.path.join(fpath, obj['urlTemplate'].replace("./",""))
            filename = os.path.basename(bigwigfile)
            bigwig_exist = check_bigwig_files(fpath+"/", filename)
            if not bigwig_exist:
                obj['track_data'] = ''
            temp_path = os.path.join(tempfile.gettempdir(),filename)
            try:
                s3.Bucket(bucket).download_file(bigwigfile, temp_path)
                bw = pyBigWig.open(temp_path)
                bw_header = bw.header()
                max_score = bw_header["maxVal"]
                bw.close()
                cap_for_read = set_cap(max_score)
                obj['max_score'] = cap_for_read
                os.remove(temp_path)
                presigned_url  = get_bigwig_type_json(bucket,bigwigfile, expires)
                obj['urlTemplate'] = presigned_url['urlTemplate']
            except Exception as e:
                logger.error("File Path: {} not found in S3".format(bigwigfile))
                pass
        #set tracks sequences
        if not obj['key'] in track_order_dict:
            continue
        obj['order'] = track_order_dict[obj['key']]
    #sort tracks using order key
    ordered_tracks = sorted(tracklist_json['tracks'], key=lambda k: k['order'])
    ordered_tracks[:] = [d for d in ordered_tracks if d.get('track_data') != '']
    tracklist_json['tracks'] = ordered_tracks
    return tracklist_json, reference_seq_url            



remove_tracks = ["Reference sequence"]

remove_tracks_php_borders = ["Reference sequence", "Genomic Map Unique Depth", \
                             "Nongenomic Map Unique Depth", "Genomic Map Repetitive Depth", \
                             "Nongenomic Map Repetitive Depth", "Junctions", "Variations", \
                             "Open MSA", "Bowtie Read Coverage", "Integrity Analysis Coverage", \
                             "Integrity Analysis - Haplotype Caller"
                            ]

def create_custom_tracks(data, ignore_tracks):
    for track_obj in data:
        if track_obj['key'] in ignore_tracks:
            track_obj.clear()
    tracks_dict_list = data
    data = [track for track in tracks_dict_list if track]

    return data


def get_tracklist_urls(fpath, map_type, track_type='sample'):
    s3 = boto3.resource('s3', region_name=cfg.aws_region)
    bucket = cfg.s3_bucket
    expires = "864000"
    s3_dir = cfg.s3_samples_key
    prefix, construct_id = os.path.split(fpath)
    fpath = os.path.join(s3_dir, prefix)
    if track_type == 'observed':
        jbrowse_dir = os.path.join(fpath, "observed", "jbrowse-results", construct_id)
    else:
        jbrowse_dir = os.path.join(fpath, "jbrowse-results", construct_id)
    response = get_s3_jbrowse_data(jbrowse_dir+"/")
    json_data = {}
    if 'Contents' not in response.keys():
        return json_data
    for item in response['Contents']:
        if item['Key'].endswith("trackList_template.json"):
            obj = s3.Object(bucket,item['Key'])
            data = obj.get()['Body'].read().decode('utf-8')
            json_data = json.loads(data)
    data , reference_seq_url = process_json(json_data, bucket, jbrowse_dir, expires, map_type, construct_id)

    if track_type == 'observed':
        #create tracks for observed map
        data['tracks'] = create_custom_tracks(data['tracks'], remove_tracks)
    
    if track_type == 'php_border':
        #create tracks for PHP borders
        data['tracks'] = create_custom_tracks(data['tracks'], remove_tracks_php_borders)
    else: 
        data['tracks'] = create_custom_tracks(data['tracks'], remove_tracks)

    data['defaultLocation'] = '{}:1..2000000'.format(construct_id)
    #create temprary trackList.json in local and upload to s3
    temp_path = os.path.join(tempfile.gettempdir(), "trackList.json")
    with open(temp_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    s3_client = boto3.client('s3', region_name=cfg.aws_region)
    dest_path = os.path.join(jbrowse_dir, "trackList.json")
    s3_client.upload_file(temp_path, bucket, dest_path)

    #return trackList presigned urls
    tracklist_presignedurl =  get_s3_presigned_url(bucket, dest_path, expires)
    tracklist_urls = {'tracklist_url': tracklist_presignedurl,  "refseq_url": reference_seq_url}

    return tracklist_urls
