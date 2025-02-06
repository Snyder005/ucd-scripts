#! /usr/bin/env python3
import sys
import time
import subprocess
import datetime
import Stage

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

def full_crosstalk_run(acq_cfg, y0):

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
    
    if pos[1] != y0:
        pos = stage.go_to_exact(y=y0)
        print(f"x = {pos[0]}, y = {pos[1]}, z = {pos[2]}")

    ## Prime lab for acquisition
    print("Get outta there! Sleeping for {0}".format(SLEEPTIME))
    time.sleep(SLEEPTIME)
    eWarning("Starting new crosstalk run.")
    set_alarm("on") # Need a way to always turn this off

    segments=['/Seg10_11', '/Seg00_01_12_13', '/Seg02_03_14_15', '/Seg04_05_16_17', '/Seg06_07'] # can remove "/"?


    

stage = Stage.Stage()

date=time.strftime("%Y%m%d")
startingimagedir='/mnt/10TBHDD/data/'+date
segments=['/Seg10_11','/Seg00_01_12_13','/Seg02_03_14_15','/Seg04_05_16_17','/Seg06_07']

y=-10212

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak.cfg',check=True, shell=True)
subprocess.run('mkdir '+startingimagedir+segments[0],check=True, shell=True)
subprocess.run('mv '+startingimagedir+'/TS_C* '+startingimagedir+segments[0],check=True, shell=True)


did_date_change=False
for i in range(4):
    date=time.strftime("%Y%m%d")
    imagedir='/mnt/10TBHDD/data/'+date        
    pos=stage.move_stage(y=y)
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak.cfg',check=True, shell=True)
    subprocess.run('mkdir '+startingimagedir+segments[i+1],check=True, shell=True)
    subprocess.run('mv '+imagedir+'/TS_C* '+startingimagedir+segments[i+1],check=True, shell=True)
    if imagedir!=startingimagedir and not did_date_change:
        did_date_change=True
        subprocess.run('mv '+startingimagedir+'/TS_C* '+startingimagedir+segments[i+1],check=True, shell=True)
        

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Finished "+segments[4]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()
subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)

