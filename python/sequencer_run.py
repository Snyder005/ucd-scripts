#!/usr/bin/env python3
import os
import glob
import time
import subprocess
import argparse
import shutil
from pathlib import Path

import pyacquire
import Email_Warning

DATADIR = '/mnt/10TBHDD/data/'

def full_sequencer_run(acq_cfg, seq_labels, sleep_time=30.0):

    ## Create acquisition directory if it does not exist
    acq_date = time.strftime("%Y%m%d")
    acq_dir = os.path.join(DATADIR, acq_date)

    Path(acq_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2(acq_cfg, acq_dir)
    shutil.copy2(os.path.realpath(__file__), acq_dir)

    ## Prime lab for acquisition
    print(f"Get outta there! Sleeping for {sleep_time}")
    time.sleep(sleep_time)
    pyacquire.email_warning("Starting new sequencer run.")
    pyacquire.set_alarm("on") # Need a way to always turn this off
    pyacquire.power_light("on") # Need a way to always turn this off

    did_date_change = False

    try:    
        for i, seq_label in enumerate(seq_labels):
           
            current_date = time.strftime("%Y%m%d")
            image_dir = os.path.join(DATADIR, current_date)

            ## Change the sequencers
            pyacquire.change_sequencer(seq_label)

            ## Begin data acquisition
            pyacquire.power_ccd('on', 'R21', bss_on=True)
            pyacquire.take_data(acq_cfg)

            ## Data management
            seq_label_dir = os.path.join(acq_dir, seq_label)
            Path(seq_label_dir).mkdir(parents=True, exist_ok=True)
            for img_file in glob.glob(os.path.join(image_dir, 'TS_C*')):
                shutil.move(img_file, os.path.join(seq_label_dir, os.path.basename(img_file)))
            if acq_dir != image_dir and not did_date_change:
                did_date_change = True
                for img_file in glob.glob(os.path.join(acq_dir, 'TS_C*')):
                    shutil.move(img_file, os.path.join(seq_label_dir, os.path.basename(img_file)))
            pyacquire.power_ccd("off", 'R21')
            pyacquire.email_warning(f"Finished sequencer run for {seq_label} {i+1}/{len(seq_labels)}")
    except Exception as e:
        pyacquire.email_warning(f"Error in sequencer run for {seq_label}")
        print(e)
    finally:
        pyacquire.power_light('off')
        pyacquire.set_alarm('off')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('acquisition_config', type=str)
    parser.add_argument('sequencer_labels', nargs='+', type=str)
    parser.add_argument('--sleep', type=float, default=30.0)
    args = parser.parse_args()

    acq_cfg = args.acquisition_config
    seq_labels = args.sequencer_labels
    sleep_time = args.sleep

    full_sequencer_run(acq_cfg, seq_labels, sleep_time=sleep_time)
