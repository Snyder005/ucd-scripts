import ShutterConfig
import time
import logging

logger = logging.getLogger(__name__)
SHUTTERDELAY = 1.0

def sanityCheck():
    
    status = ShutterConfig.status_shutter()
    logger.info(status)

def openShutter(exposure):

    sanityCheck()
    logger.info("Open shutter for {0} seconds".format(exposure))
    ShutterConfig.open_shutter()
    time.sleep(exposure)
    ShutterConfig.close_shutter()
    time.sleep(SHUTTERDELAY)
    logger.info("Shutter closed")
