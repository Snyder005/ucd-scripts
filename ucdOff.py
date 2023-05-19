#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS

CCS.setThrowExceptions(True)
fp = CCS.attachSubsystem("ucd-fp")

## Turn off back bias relay
hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
if hvSwitchOn:
    print "Setting back bias switch off."
    fp.setSynchCommand("R22/Reb0 setBackBias false")

## Check state of focal plane
ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
if ccdState == 'OFF' and hvSwitchOn:
    raise RuntimeError("CCD is powered off but back bias switch was on!")
elif ccdState == 'OFF' and not hvSwitchOn:
    raise RuntimeError("CCD is already powered off.")

## Power CCD off
fp.sendSynchCommand("R22/Reb0 powerCCDsOff")
ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
if ccdState == 'ON':
    raise RuntimeError("CCD failed to power off.")
else:
    print "CCD power {0}.".format(ccdState.lower())
