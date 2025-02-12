#!/usr/bin/env python3
import os
import glob
import time
import subprocess
import argparse
import shutil
from pathlib import Path

import pyacquire
import Stage
import Email_Warning

DATADIR = '/mnt/10TBHDD/data/'

def full_crosstalk_run(acq_cfg, dx=-10240, sleep_time=30.0):

    ## Create acquisition directory if it does not exist
    acq_date = time.strftime("%Y%m%d")
    acq_dir = os.path.join(DATADIR, acq_date)

    Path(acq_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2(acq_cfg, acq_dir)
    shutil.copy2(os.path.realpath(__file__), acq_dir)

    ## Set initial stage position
    stage = Stage.Stage()
    pos = stage.read_encoders()
    print(f"x = {pos[0]}, y = {pos[1]}, z = {pos[2]}")

    ## Prime lab for acquisition
    print("Get outta there! Sleeping for {0}".format(sleep_time))
    time.sleep(sleep_time)
    pyacquire.email_warning("Starting new crosstalk run.")
    pyacquire.set_alarm("on") # Need a way to always turn this off
    pyacquire.power_light("on") # Need a way to always turn this off

    segments = ['Seg10_11', 'Seg00_01_12_13', 'Seg02_03_14_15', 'Seg04_05_16_17', 'Seg06_07']

    ## Need to find place for try loop.
    did_date_change = False
    try:
        pyacquire.power_ccd('on', 'R21')
        for i, segment in enumerate(segments):

            current_date = time.strftime("%Y%m%d")
            image_dir = os.path.join(DATADIR, current_date)
            
            # Increment stage
            if i > 0:
                pos = stage.move_stage(x=dx)
            print(f"x = {pos[0]}, y = {pos[1]}, z = {pos[2]}")

            # Run acquisition
            pyacquire.take_data(acq_cfg)

            # Data management
            segment_dir = os.path.join(acq_dir, segment)
            Path(segment_dir).mkdir(parents=True, exist_ok=True)
            for img_file in glob.glob(os.path.join(image_dir, 'TS_C*')):
                shutil.move(img_file, os.path.join(segment_dir, os.path.basename(img_file)))
            if acq_dir != image_dir and not did_date_change:
                did_date_change = True
                for img_file in glob.glob(os.path.join(acq_dir, 'TS_C*')):
                    shutil.move(img_file, os.path.join(segment_dir, os.path.basename(img_file)))

            pyacquire.email_warning(f"Finished segment run for {segment} {i+1}/{len(segments)}")
    except Exception as e:
        pyacquire.email_warning(f"Error in segment run {segment}")
        print("Something bad happened.")
        print(e)
    finally:
        pyacquire.power_ccd('off', 'R21')
        pyacquire.power_light('off')
        pyacquire.set_alarm('off')
       
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('acq_cfg', type=str)
    parser.add_argument('--dx', type=int, default=-10240)
    parser.add_argument('--sleep', type=float, default=30.0)

    args = parser.parse_args()

    acq_cfg = args.acq_cfg
    dx = args.dx
    sleep_time = args.sleep

    full_crosstalk_run(acq_cfg, dx=dx, sleep_time=sleep_time)
