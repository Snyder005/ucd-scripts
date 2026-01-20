#!/usr/bin/env ccs-script  
#
#SHUTTER CONFIG AND FUNCTIONS FILE
#
# This is the configuration file for PS-500 camera shutter in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand. It is designed to by imported by a Jython script.
# 2023 Daniel Polin
# To Do:
# * Write class method to initialize from config file.
from xyz.froud.jvisa import JVisaResourceManager
from java.lang import String
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

    instrument = None
    """A VISA instrument (`xyz.froud.jvisa.JVisaInstrument`).
    """

    def __init__(self, resource_name=USBaddresses.shutteraddress):
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(resource_name)
        self.instrument.setWriteTerminator('\r\n')

    @classmethod
    def from_json(cls, json_file):
        pass

    def openShutter(self):
        """Opens the shutter."""
        self.instrument.queryString('$O')

    def closeShutter(self):
        """Closes the shutter."""
        self.instrument.queryString('$C')

    def reset(self):
        """Resets the shutter microcontroller."""
        self.instrument.queryString('$R')

    def home(self):
        """Puts the shutter blades in a home position."""
        self.instrument.queryString('$H')

    def status(self):
        """Reads out the status of the shutter and decodes it into readable format.

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
            raise RuntimeError("Unknown response string encountered {0}".format(response))

        return status
