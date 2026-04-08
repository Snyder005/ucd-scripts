#!/usr/bin/env ccs-script

#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.
import argparse

from ccs.scripting import CCS
from ccs.power import UCDPowerMain

def power_reb5_on():
    
    fp = CCS.attachProxy('ucd-fp')
    ucd_power = UCDPowerMain()

    ccd_state = fp.R21.Reb0.getCCDsPowerState()
    if ccd_state != 'OFF':
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

    ucd_power.power_on()

def power_reb5_off():

    fp = CCS.attachProxy('ucd-fp')
    ucd_power = UCDPowerMain()
    
    ccd_state = fp.R21.Reb0.getCCDsPowerState()
    if ccd_state != 'OFF':
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

    ucd_power.power_off()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('name', type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_false')
    args = parser.parse_args()

    state = args.on and args.off
    raftname = args.name

    if state:
        power_reb5_on(raftname)
    else:
        power_reb5_off(raftname)
