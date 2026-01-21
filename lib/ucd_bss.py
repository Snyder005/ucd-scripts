#!/usr/bin/env ccs-script

#BACK BIAS CHECK FILE

# 2025 Craig Lage
# To Do:
# * Verify usage of write terminator '\r\n'
from xyz.froud.jvisa import JVisaResourceManager

import USBaddresses

#Set termination characters where required
BK9184termination = '\r\n'

class BackBias(object):
    """A back bias voltage power supply.

    Remote connection is performed using the VISA (Virtual Instrument Software
    Architecture) API for communicating with test & measurement instruments.
    JVisa is the Java library for using VISA instruments in a Java or Jython
    program.

    Parameters
    ----------
    resource_name : `str`
        Name of resource to open.
    """

    power_supply = None
    """A power supply instrument (`xyz.froud.jvisa.JVisaInstrument`).
    """

    idn = "B&K PRECISION,9184,373B15105,2.04,0"
    """ID name of a BK Precision 9184 power supply (`str`).
    """

    def __init__(self, resource_name=USBaddresses.BK9184address):
        rm = JVisaResourceManager()
        self.power_supply = rm.openInstrument(resource_name)
        self.power_supply.setSerialBaudRate(57600)
        self.power_supply.setWriteTerminator('\r\n')
        self.power_supply.write('SYS:REM') # is this needed?

    def getIDN(self):
        """Get power supply ID name.

        Returns
        -------
        idn : `str`
            Power supply ID name.
        """
        idn = self.power_supply.queryString('*IDN?')
        return idn

    def getVoltage(self):
        """Get power supply voltage.

        Returns
        -------
        voltage : `float`
            Power supply voltage.
        """
        voltage = float(self.power_supply.queryString('MEAS:VOLT?'))
        return voltage

    def getCurrent(self):
        """Get power supply current.

        Returns
        -------
        current : `float`
            Power supply current.
        """
        current = float(self.power_supply.queryString('MEAS:CURR?'))
        return current

    def getOutputState(self):
        """Get power supply output state.

        Returns
        -------
        state : `str`
            Power supply output state.
        """
        state = self.power_supply.write('OUT?')
        return state

    def setVoltage(self, voltage):
        """Set power supply voltage.

        Parameters
        ----------
        voltage : `float`
            Power supply voltage.
        """
        self.power_supply.write('VOLT {0}'.format(voltage)

    def setVoltageLimit(self, voltage):
        """Set power supply voltage limit.

        Parameters
        ----------
        voltage : `float`
            Power supply voltage limit.
        """
        self.power_supply.write('OUT:LIM:VOLT {0}')

    def setCurrentLimit(self, current):
        """Set power supply current limit.
    
        Parameters
        ----------
        current : `float`
            Power supply current limit.
        """
        self.power_supply.write('OUT:LIM:CURR {0}')

    def setOutputState(self, state):
        """Set power supply output limit.
        
        Parameters
        ----------
        state : `bool`
            Power supply output state.
        """
        if isinstance(state, bool):
            self.power_supply.write('OUT {:d}'.format(state))
        else:
            raise ValueError('Not a boolean value: {0}'.format(state))

    def queryErrors(self):
        """Query system errors.

        Returns
        -------
        error : `str`
            System error.
        """
        error = self.power_supply.queryString('SYS:ERR?')
        return error
