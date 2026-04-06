#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the back bias voltage.
import argparse
import time

from ccs.scripting import CCS
from ccs.power import UCDPowerMain

def set_backbias_on(raftname):

    fp = CCS.attachProxy('ucd-fp', target='{0}/Reb0'.format(raftname))
    ucd_power = UCDPowerMain()

    ccd_state = fp.getCCDsPowerState()
    if ccd_state == 'ON':
        if not ucd_power.is_hvbias_on():
            ucd_power.hvbias_on()
            time.sleep(5) # delay should be implemented into power on
        if not fp.isBackBiasOn():
            fp.setBackBias(True)
    else:
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

def set_backbias_off(raftname):

    fp = CCS.attachProxy('ucd-fp', target='{0}/Reb0'.format(raftname))
    ucd_power = UCDPowerMain()

    ccd_state = fp.getCCDsPowerState()
    if ccd_state == 'ON':
        if fp.isBackBiasOn():
            fp.setBackBias(False)
        if ucd_power.is_hvbias_on():
            ucd_power.hvbias_off()
    else:
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('name', type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_true')
    args = parser.parse_args()

    raftname = args.name

    print "Not implemented yet!"
    
#    if args.on:
#        print(set_backbias_on(raftname))
#    elif args.off:
#        print(set_backbias_off(raftname))
