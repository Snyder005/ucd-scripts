#!/usr/bin/env ccs-script

#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.
import argparse
from org.lsst.ccs.scripting import CCS
import PowerSupplyConfig

def power_reb5_off(raftname):

#    fp = CCS.attachSubsystem("ucd-fp")
#    ccdState = fp.sendSynchCommand("{0}/Reb0 getCCDsPowerState".format(raftname))

#    if ccdState == 'ON':
#        raise RuntimeError("CCD is still powered on!")

    PowerSupplyConfig.power_reb5_off()

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
        PowerSupplyConfig.power_reb5_on()
    else:
        power_reb5_off(raftname)
