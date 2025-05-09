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

def full_crosstalk_run(acq_cfg, dx=-10240, dy=-10200, sleep_time=30.0, raftname='R21'):

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

    did_date_change = False
    try:
        pyacquire.power_ccd('on', raftname)
        for i, segment in enumerate(segments):

            current_date = time.strftime("%Y%m%d")
            image_dir = os.path.join(DATADIR, current_date)
            
            # Increment stage
            if i > 0:
                if raftname == 'R21':
                    pos = stage.move_stage(x=dx)
                elif raftname == 'R22':
                    pos = stage.move_stage(y=dy)
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
        print(e)
    finally:
        pyacquire.power_ccd('off', raftname)
        pyacquire.power_light('off')
        pyacquire.set_alarm('off')
       
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Automated crosstalk data run.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('acq_cfg', type=str, help="Acquisition config file.")
    parser.add_argument('--dx', type=int, default=-10240, help="Stage x increment.")
    parser.add_argument('--dy', type=int, default=-10200, help="Stage y increment.")
    parser.add_argument('-s', '--sleep', type=float, default=30.0, help="Initial sleep time.")
    parser.add_argument('-r', '--raftname', type=str, default='R21', help="Raft name (R21 or R22).")

    args = parser.parse_args()

    acq_cfg = args.acq_cfg
    raftname = args.raftname
    dx = args.dx
    dy = args.dy
    sleep_time = args.sleep

    full_crosstalk_run(acq_cfg, raftname=raftname, dx=dx, dy=dy, sleep_time=sleep_time)
