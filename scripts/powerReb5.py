#!/usr/bin/env ccs-script

#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.
import argparse
from org.lsst.ccs.scripting import CCS
from ccs.power import UCDPowerMain

ucd_power = UCDPowerMain()

def power_reb5_on(raftname):
    # To power on REB status should be off, else return with state information.
    # if not on:
    ucd_power.power_on()

def power_reb5_off(raftname):
    # To power off REB status should be on and FP state should be idle/quiescent.
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
