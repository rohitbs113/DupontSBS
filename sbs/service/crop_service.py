import logging

import sbs.database_utility as db_util
from sbs.models.Crop import Crop
from sbs.utility import log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


def add_crop(params):
    """
    Adds crop record or returns crop record if already exists
    """
    organism = params['organism']
    try:
        crop = Crop.query.filter_by(organism=organism).one_or_none()
        if crop:
            logger.info("Crop with organism [{}] already exists." \
                        .format(organism))
            return crop

        crop = Crop(organism)
        db_util.db_add_query(crop)
        db_util.db_commit()
        logger.info("Crop record for organism [{}] added successfully."
                    .format(organism))
        crop = Crop.query.filter_by(organism=organism).one_or_none()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to add Crop with error: ', e)

    return crop


def update_crop(params):
    """
    Update crop record
    """
    try:
        crop = Crop.query.get(params['id'])
        if not crop:
            raise Exception(
                'Crop not found for given id {}: '.format(params['id']))
        crop.organism = params.get('organism', crop.organism)
        db_util.db_commit()

        logger.info("Successfully updated crop for id [{}]." \
                    .format(params['id']))
        crop = Crop.query.filter_by(id=params['id']).one_or_none()
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to update Crop with error: ', e)

    return crop


def delete_crop(crop_id):
    """
    delete crop record
    """
    try:
        crop = Crop.query \
            .filter_by(id=crop_id) \
            .delete()
        db_util.db_commit()

        if crop:
            return {"status": "Deleted crop for id [{}]".format(id)}
        else:
            return {"status": "Error while deleting crop id [{}]".format(id)}
    except Exception as e:
        logger.error('An error occurred : {}'.format(str(e)))
        raise Exception('Failed to delete crop with error: ', e)
