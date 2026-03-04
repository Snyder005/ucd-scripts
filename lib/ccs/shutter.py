#!/usr/bin/env ccs-script
#
#SHUTTER CONFIG AND FUNCTIONS FILE
#
# This is the configuration file for PS-500 camera shutter in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand. It is designed to by imported by a Jython script.
# 2023 Daniel Polin
# To Do:
# * Write class method to initialize from config file.
from xyz.froud.jvisa import JVisaResourceManager, JVisaException
from ccs.device import SerialDevice

class PS500(SerialDevice):

    def __init__(self, devc_id):
        super().__init__('Sci-in Tech PS-500 Shutter', devc_id, write_terminator='\r\n')
        self.initialize()

    def initialize(self):
        """Raises JVisaException"""
        super().initialize()
        try:
            self.read_shutter_state()
        except JVisaException as e:
            self.close()
            raise e

    def open_shutter(self):
        """Open the shutter."""
        self.instrument.queryString('$O')

    def close_shutter(self):
        """Close the shutter."""
        self.instrument.queryString('$C')

    def reset_shutter(self):
        """Reset the shutter microcontroller."""
        self.instrument.queryString('$R')

    def home_shutter(self):
        """Put the shutter blades in a home position."""
        self.instrument.queryString('$H')

    def read_shutter_state(self):
        """Get the state of the shutter.

        Returns
        -------
        state : `str`
            State of the shutter in readable format.

        Raises
        ------
        JVisaException
            Raised if an unknown response string is encountered.
        """
        response = self.instrument.queryString('$B').rstrip('\x00\r\n')
        if response == '$B 9':
            state = "Shutter Open"
        elif response == '$B 10':
            state = "Closed to the right"
        elif response == '$B 5':
            state = "Closed to the left"
        elif response == '$B 8':
            state = "Opening to the left"
        elif response == '$B 1':
            state = "Opening to the right"
        else:
            raise JVisaException("Unknown response string encountered: {0}".format(response))

        return state
