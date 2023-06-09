#!/usr/bin/env ccs-script
import argparse
import sys
import time

from org.lsst.ccs.scripting import CCS
from java.time import Duration

import PowerSupplyConfig

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
        return True

    return False    

def power_ccds_off():

    fp = CCS.attachSubsystem("ucd-fp")

    ## Check state of focal plane
    hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
    ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")

    if not hvSwitchOn and ccdState == 'OFF':
        raise RuntimeError("CCD is already powered off. Back Bias relay is off.")
    elif hvSwitchOn and ccdState == 'OFF':
        print "Setting back bias switch off."
        fp.setSynchCommand("R22/Reb0 setBackBias false")
        raise RuntimeError("CCD is power off but back bias switch was on!.")
    
    if hvSwitchOn:
        fp.setSynchCommand("R22/Reb0 setBackBias false")
        PowerSupplyConfig.power_bss_off()

    hvSwitchOn = fp.sendSynchCommand("R22/Reb0 isBackBiasOn")
    if not hvSwitchOn:
        fp.sendSynchCommand("R22/Reb0 powerCCDsOff")
        print "Waiting 5.0 seconds."
        time.sleep(5.0)
        ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
        print "CCD power {0}.".format(ccdState.lower())
        return True

    return False

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_false')
    args = parser.parse_args()

    state = args.on and args.off

    if state:
        print(power_ccds_on())
    else:
        print(power_ccds_off())
