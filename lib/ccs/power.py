#!/usr/bin/env ccs-script
# This will eventually hold all power devices and UCDPower subsystem
from xyz.froud.jvisa import JVisaResourceManager, JVisaException
from ccs.device import SerialDevice

__all__ = ['BK9130B', 'BK9184']

class PowerDevice(SerialDevice):

    def read_idn(self):
        """Read the identification string of the instrument.

        Returns
        -------
        idn : `str`
            Identification string of the instrument.
        """
        idn = self.instrument.queryString('*IDN?')
        return idn

    def is_connected(self):
        """Check if the instrument is connected.

        Returns
        -------
        connected : `bool`
            `True` if the instrument is connected. `False` if not.
        """
        try:
            self.read_idn()
        except JVisaException:
            return False
        else:
            return True

    def write_all(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def write_output(self, state):
        """Write the output state of the instrument.

        Parameters
        ----------
        state : `bool`
            Output state of the instrument.

        Raises
        ------
        TypeError
            Raised if parameter ``state`` is an invalid type.
        """
        if isinstance(state, bool):
            self.instrument.write('OUTPUT {0:d}'.format(state))
        else:
            raise TypeError('Not a boolean value: {0}'.format(state))

    def power_on(self):
        self.write_all()
        self.write_output(True)

    def power_off(self):
        self.write_output(False)

class BK9184Device(PowerDevice):

    def __init__(self, devcId, voltage, max_voltage, max_current):
        super().__init__('B&K 9184 PS', devcId, baud_rate=57600, write_terminator='\r\n')
        self.voltage = voltage
        self.max_voltage = max_voltage
        self.max_current = max_current
        self.initialize()

    def initialize(self):
        super().initialize()
        try:
            self.get_idn()
            self.set_remote()
        except JVisaException as e:
            self.close()
            raise e
    
    def set_remote(self): # Add interface
        self.instrument.write('SYSTEM:REMOTE')

    def read_voltage(self):
        """Read the output voltage of the instrument.
        
        Returns
        -------
        voltage : `float`
            Output voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('MEASURE:VOLTAGE?'))
        return voltage

    def write_voltage(self):
        """Write the operating voltage to the instrument."""
        self.instrument.write('VOLTAGE {0:.3f}'.format(self.voltage))

    def read_current(self):
        """Read the output current of the instrument.

        Returns
        -------
        current : `float`
            Output current of the instrument.
        """
        current = float(self.instrument.queryString('MEASURE:CURRENT?'))
        return current

    def read_max_voltage(self):
        """Read the maximum operating voltage of the instrument.

        Returns
        -------
        max_voltage : `float`
            Maximum operating voltage of the instrument.
        """
        max_voltage = float(self.instrument.queryString('OUTPUT:LIMIT:VOLTAGE?'))
        return max_voltage

    def write_max_voltage(self):
        """Write the maximum operating voltage to the instrument."""
        self.instrument.write('OUTPUT:LIMIT:VOLTAGE {0:.3f}'.format(self.max_voltage))

    def read_max_current(self):
        """Read the maximum operating current of the instrument.

        Returns
        -------
        maxCurrent : `float`
            Maximum operating current of the instrument.
        """
        current = float(self.instrument.queryString('OUTPUT:LIMIT:CURRENT?'))

    def write_max_current(self):
        """Write the maximum operating current to the instrument."""
        self.instrument.write('OUTPUT:LIMIT:CURRENT {0:.3f}'.format(self.max_current))

    def read_output(self): # check return type (str or bool)
        """Read the output state of the instrument.

        Returns
        -------
        state : `bool`
            Output state of the instrument.
        """
        state = self.instrument.queryString('OUTPUT?')
        return state

    def write_all(self):
        """Write all operating parameters to the instrument."""
        self.write_voltage()
        self.write_max_voltage()
        self.write_max_current()

class BK9130BDevice(PowerDevice):
    
    def __init__(self, devc_id, voltages):
        super().__init__('B&K 9130B PS', devc_id, baud_rate=4800, write_terminator='\n')
        self.voltages = voltages
        self.initialize()

    def initialize(self)
        self().initialize()
        try:
            self.get_idn()
            self.set_remote()
        except JVisaException as e:
            self.close()
            raise e

    def set_remote(self):
        self.instrument.write('SYSTEM:REMOTE')

    def read_voltages(self):
        """Read the output voltages of the instrument.

        Returns
        -------
        voltages : `list` [`float`]
            Output voltages of the instrument.
        """
        voltages = [float(v) for v in self.instrument.queryString('MEASURE:VOLTAGE:ALL?').split(',')]
        return voltages

    def write_voltages(self):
        """Write the operating voltages to the instrument."""
        self.instrument.write('APPLY:VOLTAGE {0},{1},{2}'.format(*self.voltages))

    def read_output(self): # check return type (str or bool)
        """Read the output state of the instrument.

        Returns
        -------
        state : `bool`
            Output state of the instrument.
        """
        state = self.instrument.queryString('OUTPUT:STATE?')
        return state

class BK1697BDevice(PowerDevice):

    def __init__(self, devc_id, voltage):
        super().__init__('B&K 1697B PS', devc_id, write_terminator='\n')
        self.voltage = voltage
        self.initialize()

    def initialize(self)
        self().initialize()
        try:
            self.get_idn()
        except JVisaException as e:
            self.close()
            raise e

    def read_voltage(self):
        """Read the output voltage of the instrument.

        Returns
        -------
        voltage : `float`
            Output voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('VOLTAGE?'))
        return voltage

    def write_voltage(self):
        """Write the operating voltage to the instrument."""
        self.instrument.write('VOLTAGE {0:.2f}'.format(self.voltage))

    def read_output(self): # check return type
        """Read the output state of the instrument.

        Returns
        -------
        state : `bool`
            Output state of the instrument.
        """
        state = self.instrument.queryString('OUTPUT?')
        return state
