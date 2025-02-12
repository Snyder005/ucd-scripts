#! /usr/bin/env ccs-script
import argparse

from org.lsst.ccs.scripting import CCS

def change_sequencer(label):
    """Change CCD sequencer file.

    Parameters
    ----------
    label: `str`
        Sequencer label.
    """

    e2v_seq = "FP_E2V_{0}.seq".format(label)
    itl_seq = "FP_ITL_{0}.seq".format(label)

    fp = CCS.attachSubsystem("ucd-fp")
    fp.sendSynchCommand("sequencerConfig change sequencer [E2V:{0},ITL:{1}]".format(e2v_seq, itl_seq))

    output = str(fp.sendSynchCommand("getConfigurationParameterValue sequencerConfig sequencer"))
    output = output[1:-1].split(',')
    new_e2v_seq = output[0][4:]
    new_itl_seq = output[1][4:]

    if e2v_seq == new_e2v_seq and itl_seq == new_itl_seq:
        return True
    else:
        return False

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('label')
    args = parser.parse_args()

    label = args.label

    print(change_sequencer(label))
