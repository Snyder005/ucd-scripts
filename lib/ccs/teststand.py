#!/usr/bin/env ccs-script
# This will eventually hold all test stand devices and UCDBench subsystem
from ccs.device import SerialDevice

class SciinTechPS500Device(SerialDevice):
    """Interface to a Sci-in Tech model PS500 shutter device.

    Parameters
    ----------
    devc_id : `float`
        Device resource name.
    """

    def __init__(self, devc_id):
        super(SciinTechPS500Device, self).__init__('Sci-in Tech PS-500 Shutter', devc_id, baud_rate=9600,
                                                   write_terminator='\r\n', read_terminator='\r\n')
        if not self.is_closed():
            self.close_shutter()

    def is_connected(self):
        """Check if the shutter is connected.

        Returns
        -------
        connected : `bool`
            `True` if the shutter is connected. `False` if not.
        """
        if not super(SciinTechPS500Device, self).is_connected():
            return False
        try:
            state = self.read_state()
        except: # Catch known exceptions here
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
        self.query('$O')

    def close_shutter(self):
        """Close the shutter.
        """
        self.query('$C')

    def reset_shutter(self):
        """Reset the shutter microcontroller.
        """
        self.query('$R')

    def home_shutter(self):
        """Put the shutter blades in a home position.
        """
        self.query('$H')

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
        state = self.query('$B').rstrip('\x00')
        if state not in ('$B 1', '$B 5', '$B 8', '$B 9', '$B 10'):
            raise IOError("Unknown response string encountered: {0}".format(response))

        return state
