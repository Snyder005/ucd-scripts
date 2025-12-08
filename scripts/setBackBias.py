#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the back bias voltage.
import argparse
from datetime import datetime

from org.lsst.ccs.scripting import CCS

import PowerSupplyConfig
import BackBiasCheck

def set_backbias_on(raftname, vbb=PowerSupplyConfig.VN70):

    print vbb
    fp = CCS.attachSubsystem("ucd-fp")

    ## Check CCD state
    ccdState = fp.sendSynchCommand("{0}/Reb0 getCCDsPowerState".format(raftname))
    if ccdState == 'OFF':
        raise RuntimeError("CCD is not powered on!")

    PowerSupplyConfig.power_bss_on(vbb=vbb)
    print "Setting back bias switch on."
    fp.sendSynchCommand("{0}/Reb0 setBackBias True".format(raftname))

    bbs = BackBiasCheck.BackBias()
    bbs.check_connections()
    voltage = float(bbs.read_BSS())
    current = float(bbs.read_ISS())

    now = datetime.now()
    output = '{0}, Vss = {1:.4f}, Iss = {2:.4f}'.format(now, voltage, current)
    print output

    return True

def set_backbias_off(raftname):

    fp = CCS.attachSubsystem("ucd-fp")
    ccdState = fp.sendSynchCommand("{0}/Reb0 getCCDsPowerState".format(raftname))
    
    if ccdState == 'OFF':
        print "CCD was powered off but back bias was on!"

    print "Setting back bias switch off."
    fp.sendSynchCommand("{0}/Reb0 setBackBias false".format(raftname))
    PowerSupplyConfig.power_bss_off()

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
