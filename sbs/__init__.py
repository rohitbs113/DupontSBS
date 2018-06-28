from datetime import datetime
import os

from sbs.factory import create_app

app = create_app(debug=os.getenv('DEBUG', False))
import sbs.routes.routes
import sbs.routes.routes_user
import sbs.routes.routes_request
import sbs.routes.routes_sample
import sbs.routes.routes_analysis
import sbs.routes.routes_crop
import sbs.routes.routes_pipeline
import sbs.routes.routes_jbrowse
import sbs.routes.routes_variation
import sbs.routes.routes_configurator
import sbs.routes.routes_tx_method
import sbs.routes.routes_observed_map


__title__ = 'sbs'
__version__ = '0.0.1'
__author__ = 'SBS'
__author_email__ = ''
__license__ = 'Proprietary, (c) DuPont Pioneer'
__copyright__ = '(c) {}'.format(datetime.now().year)
__url__ = 'git@code.phibred.com:user/repo.git'
__description__ = """
A Flask-based API
"""

