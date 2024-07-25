from xyz.froud.jvisa import JVisaResourceManager
from java.lang import String
import USBaddresses

class Shutter():
    """A VISA optical shutter.

    Remote connection is performed using the VISA (Virtual Instrument Software
    Architecture) API for communicating with test & measurement instruments.
    JVisa is the Java library for using VISA instruments in a Java or Jython
    program.
    """

    instrument = None
    """A VISA instrument (`xyz.froud.jvisa.JVisaInstrument`).
    """

    def __init__(self):
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(USBaddresses.shutteraddress)
        self.instrument.setWriteTerminator('\r\n')

    def __init__(self):
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(USBaddresses.shutteraddress)
        self.instrument.setWriteTerminator('\r\n')

    def open(self):
        """Opens the shutter."""
        self.instrument.queryString('$O')

    def close(self):
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
        status_dict = {'$B 9' : "Shutter Open",
                       '$B 10' : "Closed to the right",
                       '$B 5' : "Closed to the left",
                       '$B 8' : "Opening to the left",
                       '$B 1' : "Opening to the right"}
        status = status_dict[response]

        return  status
