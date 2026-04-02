#!/usr/bin/env ccs-script
import argparse

from ccs.scripting import CCS

CCS.setThrowExceptions(True)

def power_ccds_on(raftname):

    fp = CCS.attachProxy("ucd-fp", target='{0}/Reb0'.format(raftname))

    ccdState = fp.getCCDsPowerState()
    if ccdState == 'ON':
        return
    elif ccdState == 'OFF':
        fp.powerCCDsOn(timeout=300)
    else:
        raise RuntimeError("invalid CCD power state: {0}".format(ccdState))

def power_ccds_off(raftname):

    fp = CCS.attachProxy("ucd-fp", target='{0}/Reb0'.format(raftname))

    ccdState = fp.getCCDsPowerState()
    if ccdState == 'OFF':
        return
    elif ccdState == 'ON':
        fp.setBackBias(False)
        fp.powerCCDsOff(timeout=300)    
    else:
        raise RuntimeError("invalid CCD power state: {0}".format(ccdState))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_true')
    args = parser.parse_args()

    raftname = args.name

    if args.on:
        power_ccds_on(raftname)
    elif args.off:
        power_ccds_off(raftname)
