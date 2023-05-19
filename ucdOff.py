#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS

fp = CCS.attachSubsystem("ucd-fp")

ccdState = 

## Check initial state
hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
if hvSwitchOn:
    print "Setting back bias switch off."
    fp.setSynchCommand("R22/Reb0 setBackBias false")

fp.sendSynchCommand("R22/Reb0 powerCCDsOff")
