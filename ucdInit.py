#!/usr/bin/env ccs-script
from org.lsst.ccs.scripting import CCS
from java.time import Duration

fp = CCS.attachSubsystem("ucd-fp")

## Check state of back bias voltage
hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
if hvSwitchOn:
    raise RuntimeError("HVBias must be off to run this script.")

## List REB voltages
print "RefP12 = {0:.1f} Volts (Positive 12 ref)".format(fp.sendSynchCommand("R22/Reb0/RefP12 getValue"))
print "RefN12 = {0:.1f} Volts (Negative 12 ref)".format(fp.sendSynchCommand("R22/Reb0/RefN12 getValue"))
print "Ref05V = {0:.1f} Volts (Positive 12 ref)".format(fp.sendSynchCommand("R22/Reb0/Ref05V getValue"))
print "Ref15V = {0:.1f} Volts (Positive 12 ref)".format(fp.sendSynchCommand("R22/Reb0/Ref15V getValue"))
print "Ref25V = {0:.1f} Volts (Positive 12 ref)".format(fp.sendSynchCommand("R22/Reb0/Ref25V getValue"))
print "Ref125V = {0:.1f} Volts (Positive 12 ref)".format(fp.sendSynchCommand("R22/Reb0/Ref125V getValue"))

## Check state of CCDs
ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
if ccdState == 'OFF':
    raise RuntimeError("CCDs must be off to run this script.")

## Modify CCD voltage limits
ccdTypes = fp.sendSynchCommand("getCCDType")
ccdType = ccdTypes["R22/Reb0"]
if ccdType == 'itl':
    fp.sendSynchCommand("R22/Reb0/Bias0 change odZeroErr 1.0")
    fp.sendSynchCommand("R22/Reb0/Bias1 change odZeroErr 1.0")
    fp.sendSynchCommand("R22/Reb0/Bias2 change odZeroErr 1.0")
    fp.sendSynchCommand("R22/Reb0/Bias0 change odTol 0.3")
    fp.sendSynchCommand("R22/Reb0/Bias1 change odTol 0.3")
    fp.sendSynchCommand("R22/Reb0/Bias2 change odTol 0.3")
    fp.sendSynchCommand("R22/Reb0/Bias1 change gdTol 0.2")

## Power CCDs On
fp.sendSynchCommand(Duration.ofSeconds(300), "R22/Reb0 powerCCDsOn")
print "CCDs power on."

## List REB voltages
print "ODV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/ODV getValue"))
print "OGV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/OGV getValue"))
print "RDV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/RDV getValue"))
print "GDV = {0:.1f} Volts".format(fp.sendSynchCommand("R22/Reb0/S00/GDV getValue"))
