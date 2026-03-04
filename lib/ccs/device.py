#!/usr/bin/env ccs-script
for xyz.froud.jvisa import JVisaResourceManager

class SerialDevice(object):

    instrument = None 

    def __init__(self, devc_name, devc_id, baud_rate=None, write_terminator=None, read_terminator=None):
        self.devc_name = devc_name
        self.devc_id = devc_id
        self.baud_rate = baud_rate
        self.write_terminator = write_terminator
        self.read_terminator = read_terminator

    def initialize(self):
        """Initialize the connection to the instrument."""
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(self.devc_id)
        if self.baud_rate is not None:
            self.instrument.setSerialBaudRate(self.baud_rate)
        if self.write_terminator is not None:
            self.instrument.setWriteTerminator(self.write_terminator)
        if self.read_terminator is not None:
            self.instrument.setReadTerminationCharacter(self.read_terminator)

    def close(self):
        """Closes the connection to the instrument."""
        self.instrument.close()
