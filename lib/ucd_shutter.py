#!/usr/bin/env ccs-script  
#
#SHUTTER CONFIG AND FUNCTIONS FILE
#
# This is the configuration file for PS-500 camera shutter in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand. It is designed to by imported by a Jython script.
# 2023 Daniel Polin
# To Do:
# * Write class method to initialize from config file.
from xyz.froud.jvisa import JVisaResourceManager

import USBaddresses

class Shutter():
    """A VISA optical shutter.

    Remote connection is performed using the VISA (Virtual Instrument Software
    Architecture) API for communicating with test & measurement instruments.
    JVisa is the Java library for using VISA instruments in a Java or Jython
    program.

    Parameters
    __________
    resource_name : `str`
        Name of resource to open.
    """

    shutter = None
    """A shutter instrument (`xyz.froud.jvisa.JVisaInstrument`).
    """

    def __init__(self, resource_name=USBaddresses.shutteraddress):
        rm = JVisaResourceManager()
        self.shutter = rm.openInstrument(resource_name)
        self.shutter.setWriteTerminator('\r\n')

    @classmethod
    def from_json(cls, json_file):
        pass

    def open(self):
        """Open the shutter."""
        self.shutter.queryString('$O')

    def close(self):
        """Close the shutter."""
        self.shutter.queryString('$C')

    def reset(self):
        """Reset the shutter microcontroller."""
        self.shutter.queryString('$R')

    def home(self):
        """Put the shutter blades in a home position."""
        self.shutter.queryString('$H')

    def getStatus(self):
        """Get the status of the shutter.

        Returns
        -------
        status : `str`
            Status of the shutter in readable format.

        Raises
        ------
        RuntimeError
            Raised if an unknown response string is encountered.
        """
        response = self.instrument.queryString('$B').rstrip('\x00\r\n')
        if response == '$B 9':
            status = "Shutter Open"
        elif response == '$B 10':
            status = "Closed to the right"
        elif response == '$B 5':
            status = "Closed to the left"
        elif response == '$B 8':
            status = "Opening to the left"
        elif response == '$B 1':
            status = "Opening to the right"
        else:
            raise RuntimeError("Unknown response string encountered: {0}".format(response))

        return status
