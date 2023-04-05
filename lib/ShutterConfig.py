#!/usr/bin/env ccs-script  

#SHUTTER CONFIG AND FUNCTIONS FILE

# This is the configuration file for PS-500 camera shutter in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand. It is designed to by imported by a Jython script.
# 2023 Daniel Polin

from xyz.froud.jvisa import JVisaResourceManager
from java.lang import String
import USBaddresses

###############################################################################

# Define the shutter commands
rm = JVisaResourceManager()
shutter = rm.openInstrument(USBaddresses.shutteraddress)
shutter.setWriteTerminator('\r\n')

def open_shutter(seconds=None):
    """Opens the shutter for a number of seconds.
    
    Args:
        seconds (float): the number of seconds to open the shutter. If None (default), the shutter will remain open until a close command is sent.
    """
    cmd = '$O'
    if seconds is not None:
        cmd += ' '+str((seconds*100)).encode()
    shutter.queryString(cmd)

def close_shutter():
    """Closes the shutter."""
    shutter.queryString('$C')

def reset_shutter():
    """Resets the shutter microcontroller."""
    shutter.queryString('$R')

def home_shutter():
    """Puts the shutter blades in a home position."""
    shutter.queryString('$H')

def status_shutter():
    """Reads out the status of the shutter and decodes it into readable format."""
    response=shutter.queryString('$B').rstrip('\x00\r\n')
    if response == '$B 9':
        return "Shutter Open"
    elif response == '$B 10':
        return "Closed to the right"
    elif response == '$B 5':
        return "Closed to the left"
    elif response == '$B 8':
        return "Opening to the left"
    elif response == '$B 1':
        return "Opening to the right"
