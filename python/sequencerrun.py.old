#!/usr/bin/env python3
import numpy as np
import time
import subprocess
import glob
import argparse
import os
import shutil

from astropy.io import fits
from pathlib import Path

import Email_Warning

SLEEPTIME = 30.0
DATADIR = '/mnt/10TBHDD/data/'

def set_alarm(state):
    """Set alarm state.

    Parameters
    ----------
    state : `str`
        Alarm state (must be either 'On' or 'Off', case-insensitive).
    
    Raises
    ------
    ValueError
        Raised if state is an invalid choice.
    """
    if state.lower() == "off":
        subprocess.run('python /home/ccd/security/disarm.py', check=True, shell=True)
    elif state.lower() == "on":
        subprocess.run('python /home/ccd/security/arm.py', check=True, shell=True)
    else:
        raise ValueError(f"{state} must be either 'On' or 'Off'")

def power_light(state):
    """Set lamp state.

    Parameters
    ----------
    state : `str`
        Lamp state (must be either 'On' or 'Off', case-insensitive).

    Raises
    ------
    ValueError
        Raised if state is an invalid choice.
    """
    if state.lower() == "off":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py', check=True, shell=True)
    elif state.lower() == "on":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOn.py', check=True, shell=True)
    else:
        raise ValueError(f"{state} must be either 'On' or 'Off'")

def take_data(acq_cfg):
    """Perform data acquisition.

    Parameters
    ----------
    acq_cfg: `str`
        Acquisition configuration file.
    """
    subprocess.run(f'ccs-script /home/ccd/ucd-scripts/ucd-data.py {acq_cfg}', check=True, shell=True)

def power_CCD(state):
    """Set CCD power state.

    Parameters
    ----------
    state : `str`
        CCD power state (must be either 'On' or 'Off', case-insensitive).

    Raises
    ------
    ValueError
        Raised if state is an invalid choice.
    """
    if state.lower() == "off":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py R21 --off', check=True, 
                       shell=True)
        time.sleep(2)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py R21 --off',check=True, 
                       shell=True)
    elif state.lower() == "on":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py R21 --on',check=True, 
                       shell=True)
        time.sleep(2)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py R21 --on',check=True, 
                       shell=True)
    else:
        raise ValueError(f"{state} must be either 'On' or 'Off'")

def get_sequencer():
    ## Maybe make this a jython function
    output = subprocess.check_output(["ccs-shell <ccssequencercheck.txt"], shell=True, text=True)
    seq_configs = output.splitlines()[-2][1:-1].split(',')    
    e2v_seq = seq_configs[0][4:]
    itl_seq = seq_configs[1][4:]
#    print(output)

    return e2v_seq, itl_seq

def change_sequencer(e2v_seq, itl_seq):
    text='''set target ucd-fp

sequencerConfig change sequencer [E2V:{0},ITL:{1}]

printConfigurationParameters Sequencer'''.format(e2v_seq, itl_seq)
#    text = "ucd-fp/sequencerConfig change sequencer [E2V:{0},ITL:{1}]".format(e2v_seq, itl_seq)
    file = open("ccssequencercommands.txt", 'w')
    file.write(text)       
    file.close()
    
    output = subprocess.check_output(["ccs-shell <ccssequencercommands.txt"], shell=True)
#    print(output)

    if (e2v_seq, itl_seq) == get_sequencer():
        return True
    else:
        return False

def change_sequencer2(e2v_seq, itl_seq):
    text = "ucd-fp/sequencerConfig change sequencer [E2V:{0},ITL:{1}]".format(e2v_seq, itl_seq)
    file = open("ccssequencercommands.txt", 'w')
    file.write(text)       
    file.close()
    
    output = subprocess.check_output(["ccs-shell <ccssequencercommands.txt"], shell=True)
    print(output)

    if (e2v_seq, itl_seq) == get_sequencer():
        return True
    else:
        return False

def eWarning(warning):

    try:
        subject = "Run Update" + time.asctime()
        w_file = open('/home/ccd/ucd-scripts/python/send_warning', 'w')
        w_file.write(subject + ":: ")
        w_file.write(warning)
        w_file.close()
        Email_Warning.Send_Warning(subject, warning)
    except:
        pass
        
def get_sequencer_from_header(directory):

    fits_files = glob.glob(os.path.join(directory, '*.fits'))
    header_seq = fits.getheader(fits_files[0])['SEQFILE']

    return header_seq

def full_sequencer_run(acq_cfg, seq_labels, dry_run=False):

    ## Create acquisition directory if it does not exist
    acq_date = time.strftime("%Y%m%d")
    acq_dir = os.path.join(DATADIR, acq_date)

    Path(acq_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2(acq_cfg, acq_dir)
    shutil.copy2(os.path.realpath(__file__), acq_dir)

    ## Prime lab for acquisition
    print("Get outta there! Sleeping for {0}".format(SLEEPTIME))
    time.sleep(SLEEPTIME)
    eWarning("Starting new sequencer run.")
    set_alarm("on") # Need a way to always turn this off

    ## Begin sequencer acquisitions
    for i, seq_label in enumerate(seq_labels):
       
        e2v_seq = 'FP_E2V_{0}.seq'.format(seq_label)
        itl_seq = 'FP_ITL_{0}.seq'.format(seq_label)

        ## Change the sequencers
        attempt = 0
        while attempt < 5: # can eliminate?
            try:
                if change_sequencer(e2v_seq, itl_seq):
                    break
            except:
                time.sleep(10)
            finally:
                attempt += 1
        else:
            eWarning(f"Sequencer failed to update to [E2V:{e2v_seq},ITL:{itl_seq}]")
            raise Exception(f"Sequencer failed to update to [E2V:{e2v_seq},ITL:{itl_seq}]")

        ## Begin data acquisition
        power_CCD("on")
        try:
            take_data(acq_cfg)
            header_seq = get_sequencer_from_header(acq_dir)

            if header_seq not in (e2v_seq, itl_seq):
                eWarning("Sequencer file is not correct in the header!")
                time.sleep(2)
                raise Exception("Sequencer file not correct in the header!")

            ## Create a new subdirectory named after the sequencer label
            seq_label_dir = os.path.join(acq_dir, seq_label)
            Path(seq_label_dir).mkdir(parents=True, exist_ok=True)

            ## Move image files to the new subdirectory
            for img_file in glob.glob(os.path.join(acq_dir, 'TS_C*')):
                shutil.move(img_file, os.path.join(seq_label_dir, os.path.basename(img_file)))
            
            eWarning(f"Finished sequencer run for {seq_label} {i+1}/{len(seq_labels)}")
            time.sleep(10)
        except Exception as e:
            eWarning(f"Error in sequencer run on {seq_label}")
            power_light("off")
        finally:
            power_CCD("off")
    set_alarm("off")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('acquisition_config', type=str)
    parser.add_argument('sequencer_labels', nargs='+', type=str)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    full_sequencer_run(args.acquisition_config, args.sequencer_labels, args.dry_run)
