import logging

import sbs.database_utility as db_util
from sbs.models.TxMethod import TxMethod
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def add_tx_method(params):
    """
    Adds tx_method record or returns tx_method record if already exists
    """
    method_name = params['tx_method']
    try:
        tx_method = TxMethod.query.filter_by(method_name=method_name) \
            .one_or_none()

        if tx_method:
            logger.info("TxMethod with method name [{}] already exists."
                        .format(method_name))
            return tx_method

        tx_method = TxMethod(method_name)
        db_util.db_add_query(tx_method)
        db_util.db_commit()
        logger.info("Transformation method record for method {} added successfully."
                    .format(method_name))
        tx_method = TxMethod.query.filter_by(method_name=method_name) \
            .one_or_none()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to fetch Transformation method id for method '
                        '[{}] with error {} '.format(method_name, e))

    return tx_method
