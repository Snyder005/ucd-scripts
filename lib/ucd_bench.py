import ShutterConfig
import time

SHUTTERDELAY = 1.0

def sanityCheck():
    
    status = ShutterConfig.status_shutter()
    print status

def openShutter(exposure):

    sanityCheck()
    print "Open shutter for {0} seconds".format(exposure)
    ShutterConfig.open_shutter()
    time.sleep(exposure)
    ShutterConfig.close_shutter()
    time.sleep(SHUTTERDELAY)
    print "Shutter closed"
