#!/usr/bin/env ccs-script
import argparse

from ccs.scripting import CCS

CCS.setThrowExceptions(True)

def power_ccds_on():

    fp = CCS.attachProxy("ucd-fp")

    ccd_state = fp.R21.Reb0.getCCDsPowerState()
    if ccd_state == 'ON':
        return
    elif ccd_state == 'OFF':
        fp.R21.Reb0.powerCCDsOn(timeout=300)
    else:
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

def power_ccds_off():

    fp = CCS.attachProxy("ucd-fp")

    ccd_state = fp.R21.Reb0.getCCDsPowerState()
    if ccd_state == 'OFF':
        return
    elif ccd_state == 'ON':
        fp.R21.Reb0.setBackBias(False)
        fp.R21.Reb0.powerCCDsOff(timeout=300)
    else:
        raise RuntimeError("invalid CCD power state: {0}".format(ccd_state))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_true')
    args = parser.parse_args()

    if args.on:
        power_ccds_on()
    elif args.off:
        power_ccds_off()
