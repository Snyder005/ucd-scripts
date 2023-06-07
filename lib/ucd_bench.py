import time
import logging
import SphereConfig
import ShutterConfig

logger = logging.getLogger(__name__)
SHUTTERDELAY = 1.0

shutter = ShutterConfig.Shutter()
sphere = SphereConfig.Sphere()

def sanityCheck():
    
    status = shutter.status()
    logger.debug(status)

def openShutter(exposure):

    try:
        sanityCheck()
    except RuntimeError:
        logger.warning("Shutter in unknown state, attempting to close.")
        shutter.close()
        time.sleep(SHUTTERDELAY)
    logger.debug("Open shutter for {0} seconds".format(exposure))
    shutter.open()
    time.sleep(exposure)
    shutter.close()
    time.sleep(SHUTTERDELAY)
    logger.debug("Shutter closed")

def turnLightOn():

    logger.debug("Turning on light.")
    sphere.turn_light_on()

def turnLightOff():

    logger.debug("Turning off light.")
    sphere.turn_light_off()

def setLightIntensity(intensity):

    logger.debug("Setting light intensity to {0}%".format(intensity))
    sphere.set_light_intensity(intensity)

def readPhotodiodeCurrent():

    logger.debug("Reading photodiode current.")
    return sphere.read_photodiode()
