#!/usr/bin/env ccs-script
#
#SHUTTER CONFIG AND FUNCTIONS FILE
#
# This is the configuration file for PS-500 camera shutter in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand. It is designed to by imported by a Jython script.
# 2023 Daniel Polin
# To Do:
# * Write class method to initialize from config file.
from xyz.froud.jvisa import JVisaException
from ccs.device import SerialDevice

class SciinTechPS500Device(SerialDevice):
    """Interface to a Sci-in Tech model PS500 shutter device.

    Parameters
    ----------
    devc_id : `float`
        Device resource name.
    """

    def __init__(self, devc_id):
        super(SciinTechPS500Device, self).__init__('Sci-in Tech PS-500 Shutter', devc_id, write_terminator='\r\n')
        if not self.is_shutter_closed():
            self.close_shutter()

    def is_connected(self):
        """Check if the shutter is connected.

        Returns
        -------
        connected : `bool`
            `True` if the shutter is connected. `False` if not.
        """
        try:
            state = self.read_state()
        except JVisaException:
            return False
        else:
            return True

    def is_closed(self):
        """Check if the shutter is closed.

        Returns
        -------
        is_closed : `bool`
           `True` if the shutter is closed. `False` if not.
        """
        state = self.read_state()
        if (state == '$B 5') or (state == '$B 10'):
            return True
        else:
            return False

    def open_shutter(self):
        """Open the shutter.
        """
        self.instrument.queryString('$O')

    def close_shutter(self):
        """Close the shutter.
        """
        self.instrument.queryString('$C')

    def reset_shutter(self):
        """Reset the shutter microcontroller.
        """
        self.instrument.queryString('$R')

    def home_shutter(self):
        """Put the shutter blades in a home position.
        """
        self.instrument.queryString('$H')

    def read_state(self):
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
        state = self.instrument.queryString('$B').rstrip('\x00\r\n')
        if state not in ('$B 1', '$B 5', '$B 8', '$B 9', '$B 10'):
            raise JVisaException("Unknown response string encountered: {0}".format(response))

        return state
