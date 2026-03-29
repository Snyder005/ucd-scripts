#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the back bias voltage.
import argparse
from datetime import datetime

from org.lsst.ccs.scripting import CCS
from ccs.power import UCDPowerMain

def set_backbias_on(raftname):
    # To power on CCD should be on.

    # Connect control systems
    fp = CCS.attachSubsystem("ucd-fp")
    ucd_power = UCDPowerMain()

    ## Check CCD state
    ccdState = fp.sendSynchCommand("{0}/Reb0 getCCDsPowerState".format(raftname))
    if ccdState == 'OFF':
        raise RuntimeError("CCD is not powered on!")

    # Power on HVBias power supply
    ucd_power.hvbias_on()

    # Set back bias switch on
    print "Setting back bias switch on."
    fp.sendSynchCommand("{0}/Reb0 setBackBias True".format(raftname))

    # Print HVBias state
    name, state, voltage, current = ucd_power.hvbias_control.get_state()
    print '{0}: State = {1}, voltage = {2:.3f} V, current = {3:.3f} A'.format(name, state, voltage, current))

    return True

def set_backbias_off(raftname):

    # Connect control systems
    fp = CCS.attachSubsystem("ucd-fp")
    ucd_power = UCDPowerMain()

    print "Setting back bias switch off."
    fp.sendSynchCommand("{0}/Reb0 setBackBias false".format(raftname))
    ucd_power.hvbias_off()

    # Print HVBias state
    name, state, voltage, current = ucd_power.hvbias_control.get_state()
    print '{0}: State = {1}, voltage = {2:.3f} V, current = {3:.3f} A'.format(name, state, voltage, current))

    return True

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('name', type=str)
    parser.add_argument('--vbb', type=float, default=PowerSupplyConfig.VN70)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_false')
    args = parser.parse_args()

    state = args.on and args.off
    raftname = args.name
    vbb = args.vbb

    if state:
        print(set_backbias_on(raftname, vbb=vbb))
    else:
        print(set_backbias_off(raftname))
