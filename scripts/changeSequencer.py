#! /usr/bin/env ccs-script
import argparse

from ccs.scripting import CCS

def change_sequencer(label):
    """Change CCD sequencer file.

    Parameters
    ----------
    label: `str`
        Sequencer label.
    """
    fp = CCS.attachProxy('ucd-fp')

    new_seq = '[E2V:FP_E2V_{0}.seq,ITL:FP_ITL_{0}.seq]'.format(label)
    fp.sequencerConfig.change('sequencer', new_seq)

    seq = str(fp.getConfigurationParameterValue('sequencerConfig', 'sequencer')
    if new_seq != seq:
        raise RuntimeError("failed to update sequencer: {0}".format(label))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('label')
    args = parser.parse_args()

    label = args.label

    print(change_sequencer(label))
