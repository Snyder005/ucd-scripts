#! /usr/bin/env python3
import subprocess
import time

import Email_Warning

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
    state = state.lower()
    if state in ['on', 'off']:
        subprocess.run(f"ccs-script /home/ccd/ucd-scripts/scripts/powerSphere.py --{state}",
                       check=True, shell=True)
    else:
        raise ValueError(f"{state} must be either 'on' or 'off'")

def set_bss(state, raftname):
    """Set back bias state. 
 
    Parameters 
    ---------- 
    state : `str` 
        CCD power state (must be either 'on' or 'off', case-insensitive).
    raftname: `str`
        Raft name (must be either 'R21' or 'R22').
 
    Raises 
    ------ 
    ValueError 
        Raised if state is an invalid choice.
    """
    if state.lower() == "off":
        subprocess.run(f"ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py {raftname} --off", 
                       check=True, shell=True)
    elif state.lower() == "on":
        subprocess.run(f"ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py {raftname} --on",
                       check=True, shell=True)
    else:
        raise ValueError(f"{state} must be either 'On' or 'Off'")

def power_ccd(state, raftname, bss_on=True): 
    """Set CCD power state. 
 
    Parameters 
    ---------- 
    state : `str` 
        CCD power state (must be either 'on' or 'off', case-insensitive).
    raftname: `str`
        Raft name (must be either 'R21' or 'R22').
    bss_on : `bool`
        Set back bias state to on (Default is True).
 
    Raises 
    ------ 
    ValueError 
        Raised if state is an invalid choice. 
    """
    if state.lower() == "off":
        set_bss('off', raftname)
        subprocess.run(f"ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py {raftname} --off", 
                       check=True, shell=True)
    elif state.lower() == "on":
        subprocess.run(f"ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py {raftname} --on",
                       check=True, shell=True)
        time.sleep(2)
        if bss_on:
            set_bss('on', raftname)
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

def change_sequencer(seq_label):
    """Change CCD sequencer file.

    Parameters
    ----------
    seq_label: `str`
        Naming label for the CCD sequencer files.
    """
    subprocess.run(f'ccs-script /home/ccd/ucd-scripts/scripts/changeSequencer.py {seq_label}',
                   check=True, shell=True)

def email_warning(warning):
    """Email a warning message.

    Parameters
    ----------
    warning: `str`
        Warning message to email.
    """ 
    try:
        subject = "Run Update" + time.asctime()
        w_file = open('/home/ccd/ucd-scripts/python/send_warning', 'w')
        w_file.write(subject + ":: ")
        w_file.write(warning)
        w_file.close()
        Email_Warning.Send_Warning(subject, warning)
    except:
        pass
