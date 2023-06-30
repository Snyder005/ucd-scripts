#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS

CCS.setThrowExceptions(True)

def power_ccds_off():

    fp = CCS.attachSubsystem("ucd-fp")


    ## Get state of focal plane
    hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
    ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")

    if hvSwitchOn and ccdState == 'OFF':
        fp.setSynchCommand("R22/Reb0 setBackBias false")
        raise RuntimeError("CCD is power off but back bias switch was on!")
    elif hvSwitchOff and ccdState == 'OFF':
        raise RuntimeError("CCD is powered off and back bias switch is off.")
    
    if hvSwitchOn:
        print "Setting back bias switch off."
        fp.setSynchCommand("R22/Reb0 setBackBias false")

#    if hvOn:
#        print "Setting back bias power off."

    hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
    if not hvSwitchOn:
        fp.sendSynchCommand("R22/Reb0 powerCCDsOff")
        ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
        print "CCD power {0}".format(ccdState.lower()) 

if __name__ == '__main__':

    power_ccds_off()
