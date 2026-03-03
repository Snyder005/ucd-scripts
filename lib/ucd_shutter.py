#!/usr/bin/env ccs-script
#
#SHUTTER CONFIG AND FUNCTIONS FILE
#
# This is the configuration file for PS-500 camera shutter in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand. It is designed to by imported by a Jython script.
# 2023 Daniel Polin
# To Do:
# * Write class method to initialize from config file.
from xyz.froud.jvisa import JVisaResourceManager

class Device(object):

    instrument = None 

    baudRate = None
    writeTerminator = None
    readTerminator = None

    def __init__(self, devcName, devcId):
        self.devcName = devcName
        self.devcId = devcId

    def initialize(self):
        """Initialize the connection to the instrument."""
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(self.devcId)
        if self.baudRate is not None:
            self.instrument.setSerialBaudRate(self.baudRate)
        if self.writeTerminator is not None:
            self.instrument.setWriteTerminator(self.writeTerminator)
        if self.readTerminator is not None:
            self.instrument.setReadTerminationCharacter(self.readTerminator)

    def close(self):
        """Closes the connection to the instrument."""
        self.instrument.close()

class Shutter(Device):

    def __init__(self, devcId):
        self.writeTerminator = '\r\n'

        super().__init__('Sci-in Tech PS-500 Shutter', devcId)
        self.initialize()

    def initialize(self):
        """Raises JVisaException"""
        super().initialize()
        try:
            self.readShutterState()
        except JVisaException as e:
            self.close()
            raise e

    def openShutter(self):
        """Open the shutter."""
        self.shutter.queryString('$O')

    def closeShutter(self):
        """Close the shutter."""
        self.shutter.queryString('$C')

    def resetShutter(self):
        """Reset the shutter microcontroller."""
        self.shutter.queryString('$R')

    def homeShutter(self):
        """Put the shutter blades in a home position."""
        self.shutter.queryString('$H')

    def readShutterState(self):
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
