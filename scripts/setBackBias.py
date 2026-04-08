#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the back bias voltage.
import argparse
import time

from ccs.scripting import CCS
from ccs.power import UCDPowerMain

def set_backbias_on():

    fp = CCS.attachProxy('ucd-fp')
    ucd_power = UCDPowerMain()

    ccd_state = fp.R21.Reb0.getCCDsPowerState()
    if ccd_state != 'ON':
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

    if not ucd_power.is_hvbias_on():
        ucd_power.hvbias_on()
        time.sleep(5)

    if not fp.R21.Reb0.isBackBiasOn():
        fp.clear(15)
        fp.R21.Reb0.setBackBias(True)

def set_backbias_off():

    fp = CCS.attachProxy('ucd-fp')
    ucd_power = UCDPowerMain()

    ccd_state = fp.R21.Reb0.getCCDsPowerState()
    if ccd_state != 'ON':
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

    if fp.R21.Reb0.isBackBiasOn():
        fp.clear(15)
        fp.R21.Reb0.setBackBias(False)

    if ucd_power.is_hvbias_on():
        ucd_power.hvbias_off()
        time.sleep(5)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_true')
    args = parser.parse_args()
    
    if args.on:
        set_backbias_on()
    elif args.off:
        set_backbias_off()
