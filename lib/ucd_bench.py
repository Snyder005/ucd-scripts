# Initialize bench subsystem.
# Includes functions to interface with the subsystem and add logging
import time
import logging
import SphereConfig
#import ShutterConfig
from ccs.teststand import SciinTechPS500Device

logger = logging.getLogger(__name__)
SHUTTERDELAY = 1.0

shutter = SciinTechPS500Device('/dev/serial/by-path/pci-0000:00:14.0-usb-0:7.1.4:1.0-port0')
sphere = SphereConfig.Sphere()

def sanityCheck():
    
    state = shutter.read_state()
    logger.debug(state)

def openShutter(exposure):

    try:
        sanityCheck()
    except RuntimeError:
        logger.warning("Shutter in unknown state, resetting and attempting to close.")
        shutter.reset_shutter()
        time.sleep(4)
        shutter.close_shutter()
        time.sleep(SHUTTERDELAY)
    logger.debug("Open shutter for {0} seconds".format(exposure))
    shutter.open_shutter()
    time.sleep(exposure)
    shutter.close_shutter()
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
