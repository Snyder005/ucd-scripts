#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the back bias voltage.
import argparse
from org.lsst.ccs.scripting import CCS

import PowerSupplyConfig

def set_backbias_on():

    fp = CCS.attachSubsystem("ucd-fp")

    ## Check CCD state
    ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
    if ccdState == 'OFF':
        raise RuntimeError("CCD is not powered on!")

    PowerSupplyConfig.power_bss_on()
    print "Setting back bias switch on."
    fp.sendSynchCommand("R22/Reb0 setBackBias True")

    return True

def set_backbias_off():

    fp = CCS.attachSubsystem("ucd-fp")
    ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
    
    if ccdState == 'OFF':
        print "CCD was powered off but back bias was on!"

    print "Setting back bias switch off."
    fp.sendSynchCommand("R22/Reb0 setBackBias false")
    PowerSupplyConfig.power_bss_off()

    return True

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_false')
    args = parser.parse_args()

    state = args.on and args.off

    if state:
        print(set_backbias_on())
    else:
        print(set_backbias_off())
