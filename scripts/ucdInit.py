#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS
from java.time import Duration

CCS.setThrowExceptions(True)

def power_ccds_on():

    fp = CCS.attachSubsystem("ucd-fp")

    ## Check state of focal plane
    hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
    ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")

    if hvSwitchOn and ccdState == 'ON':
        raise RuntimeError("CCD is already powered on. Back Bias relay is on.")
    elif not hvSwitchOn and ccdState == 'ON':
        raise RuntimeError("CCD is already powered on. Back Bias relay is off.")
    elif hvSwitchOn and ccdState == 'OFF':
        print "Setting back bias switch off."
        fp.setSynchCommand("R22/Reb0 setBackBias false")
        raise RuntimeError("CCD is powered off but back bias switch was on!")

    ## Power CCDs On
    hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
    if not hvSwitchOn:
        fp.sendSynchCommand(Duration.ofSeconds(300), "R22/Reb0 powerCCDsOn")
        ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
        print "CCD power {0}.".format(ccdState.lower())
        print "ODV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/ODV getValue"))
        print "OGV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/OGV getValue"))
        print "RDV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/RDV getValue"))
        print "GDV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/GDV getValue"))

if __name__ == '__main__':

    power_ccds_on()
