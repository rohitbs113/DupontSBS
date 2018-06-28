import os

dafault_stage = 'sb'
stage = os.environ.get('STAGE') or dafault_stage

# Database properties
db_username = '#{DB_USERNAME}'
db_password = '#{DB_PASSWORD}'
db_username_deploy = '#{DB_USERNAME_DEPLOY}'
db_password_deploy = '#{DB_PASSWORD_DEPLOY}'
db_name = '#{DB_INSTANCE}'
db_endpoint = '#{DB_CONN_URL}'
version = '#{Octopus.Release.Number}'

# SQLAlchemy properties
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# OIDC properties
REQUIRE_ROLE = True
if os.environ.get('REQUIRE_ROLE') == 'False':
    REQUIRE_ROLE = False

s3_bucket = os.environ.get("s3_bucket") 
s3_samples_key = os.environ.get("s3_samples_key") 
domain_url = os.environ.get("domain_url") 
aws_credential_url = os.environ.get("aws_credential_url")
role_name = os.environ.get("role_name")
samtools_path = os.environ.get("samtools_path")

recal_queue = os.environ.get("sbs_pipeline_batch_recal_queue_stack_name")
main_queue = os.environ.get("sbs_pipeline_batch_main_queue_stack_name")
quick_queue = os.environ.get("sbs_pipeline_batch_quick_queue_stack_name")
rt_jobdef_name = os.environ.get("sbs_pipeline_batch_rt_jobdef_name")
wt_jobdef_name = os.environ.get("sbs_pipeline_batch_wt_jobdef_name")
je_jobdef_name = os.environ.get("sbs_pipeline_batch_je_jobdef_name")
ic_jobdef_name = os.environ.get("sbs_pipeline_batch_ic_jobdef_name")
gd_jobdef_name = os.environ.get("sbs_pipeline_batch_gd_jobdef_name")
dd_jobdef_name = os.environ.get("sbs_pipeline_batch_dd_jobdef_name")
log_level = os.environ.get('log_level') or 'INFO'
lab_role = 'lab'
client_role = 'client'
aws_region = os.environ.get('region')

# regenerate observed map properties
analysis_read_dir_observed = "observed"
analysis_read_dir_expected = "output"

