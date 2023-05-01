#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS
from org.lsst.ccs.bus.states import AlertState
from org.lsst.ccs.subsystem.focalplane.states import FocalPlaneState
from java.time import Duration
from ccs import proxies
import time
CLEARDELAY = 0.07

fp = CCS.attachProxy("ucd-fp")
agentName = fp.getAgentProperty("agentName")
if agentName != "ucd-fp":
    fp = CCS.attachProxy(agentName)
imageTimeout = Duration.ofSeconds(60)

def sanityCheck():

    state = fp.getState()
    alert = state.getState(AlertState)
    if alert != AlertState.NOMINAL:
        print "Warning: {0} subsystem is in alert state {1}".format(agentName, alert)

def clear(n=1):

    if n == 0:
        return
    print "Clearing CCDs {0:d}".format(n)
    fp.clear(n)
    fp.waitForSequencer(Duration.ofSeconds(2))

def takeExposure(exposeCommand=None, fitsHeaderData=None, annotation=None, locations=None, clears=1):

    sanityCheck()
    print "Setting Fits headers {0}".format(fitsHeaderData)
    fp.setHeaderKeywords(fitsHeaderData)
    clear(clears)
    fp.startIntegration(annotation, locations)

    if exposeCommand:
        extraData = exposeCommand()
        if extraData:
            fp.setHeaderKeywords(extraData)

    try:

        fp.endIntegration()
        im = fp.waitForFitsFiles(imageTimeout)
    except:
        raise

    return im
