#!/usr/bin/env ccs-script
for xyz.froud.jvisa import JVisaResourceManager, JVisaException

class SerialDevice(object):
    """Interface to a SCPI-commanded device.

    Parameters
    ----------
    devc_name : `str`
        Device name.
    devc_id : `str`
        Device resource name.
    baud_rate : `int`, optional
        Serial baud rate.
    write_terminator : `str`, optional
        Write command terminator.
    read_terminator : `str`, optional
        Read operation terminator.
    """

    def __init__(self, devc_name, devc_id, baud_rate=None, write_terminator=None, read_terminator=None):
        self._devc_name = devc_name
        self._devc_id = devc_id
        self._baud_rate = baud_rate
        self._write_terminator = write_terminator
        self._read_terminator = read_terminator
        self.initialize()

    @property
    def devc_name(self):
        """Device name (`str`).
        """
        return self._devc_name

    @property
    def devc_id(self):
        """Device resource name (`str`).
        """
        return self._devc_id

    @property
    def baud_rate(self):
        """Serial baud rate (`int`).
        """
        return self._baud_rate

    @property
    def write_terminator(self):
        """Write command terminator (`str`).
        """
        return self._write_terminator

    @property
    def read_terminator(self):
        """Read operation terminator (`self`).
        """
        return self._read_terminator

    @property
    def instrument(self):
        """A VISA instrument (`xyz.froud.jvisa.JVisaInstrument`).
        """
        return self._instrument

    def initialize(self):
        """Initialize the connection to the instrument.

        Raises
        ------
        JVisaException
            Raised if there is an error communicating with the device.
        """
        rm = JVisaResourceManager()
        self._instrument = rm.openInstrument(self.devc_id)
        if self.baud_rate is not None:
            self.instrument.setSerialBaudRate(self.baud_rate)
        if self.write_terminator is not None:
            self.instrument.setWriteTerminator(self.write_terminator)
        if self.read_terminator is not None:
            self.instrument.setReadTerminationCharacter(self.read_terminator)
        
        if not self.is_connected():
            self.close()
            raise JVisaException("Error communicating with device: {0}".format(self.devc_name)) 

    def close(self):
        """Closes the connection to the instrument."""
        try:
            self.instrument.close()
        except JVisaException:
            pass

    def is_connected(self):
        """Check if the instrument is connected.

        Raises
        ------
        NotImplementedError
            Raised if not implemented in child class.
        """
        raise NotImplementedError
