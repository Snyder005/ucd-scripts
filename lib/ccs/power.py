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
        idn = str(self.instrument.queryString('*IDN?'))
        return idn

    def is_connected(self):
        """Check if the instrument is connected.

        Returns
        -------
        connected : `bool`
            `True` if the instrument is connected. `False` if not.
        """
        try:
            idn = self.read_idn()
        except JVisaException:
            return False
        else:
            return True

class BK9184Device(PowerDevice):
    """Interface to a B&K model 9184 power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    voltage : `float`
        Default operating voltage of the instrument.
    max_voltage : `float`
        Default maximum voltage of the instrument.
    max_current : `float`
        Default maximum current of the instrument.
    """

    def __init__(self, devc_id, voltage, max_voltage, max_current):
        self._voltage = voltage
        self._max_voltage = max_voltage
        self._max_current = max_current
        super().__init__('B&K 9184 PS', devc_id, baud_rate=57600, write_terminator='\r\n')

    @property
    def voltage(self):
        """Defaut operating voltage (`float`).
        """
        return self._voltage

    @property
    def max_voltage(self):
        """Default maximum voltage (`float`).
        """
        return self._max_voltage

    @property
    def max_current(self):
        """Default maximum current (`float`).
        """
        return self._max_current
   
    def get_voltage(self):
        """Get the setpoint voltage of the instrument.

        Returns
        -------
        voltage : `float`
            Setpoint voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('VOLTAGE?'))
        return voltage

    def read_voltage(self):
        """Read the output voltage of the instrument.
        
        Returns
        -------
        voltage : `float`
            Output voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('MEASURE:VOLTAGE?'))
        return voltage

    def write_voltage(self, voltage=None):
        """Write the setpoint voltage to the instrument.

        Parameters
        ----------
        voltage : `float`
            Setpoint voltage of the instrument (the default operating voltage,
            by default)
        """
        if voltage is None:
            voltage = self.voltage
        self.instrument.write('VOLTAGE {0:.3f}'.format(voltage))

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

    def write_max_voltage(self, voltage=None):
        """Write the maximum setpoint voltage to the instrument.

        Parameters
        ----------
        voltage : `float`, optional
            Maximum setpoint voltage of the instrument (the default maximum
            voltage, by default).
        """
        if voltage is None:
            voltage = self.max_voltage
        self.instrument.write('OUTPUT:LIMIT:VOLTAGE {0:.3f}'.format(voltage))

    def read_max_current(self):
        """Read the maximum operating current of the instrument.

        Returns
        -------
        max_current : `float`
            Maximum operating current of the instrument.
        """
        max_current = float(self.instrument.queryString('OUTPUT:LIMIT:CURRENT?'))
        return max_current

    def write_max_current(self, current=None):
        """Write the maximum setpoint current to the instrument.

        Parameters
        ----------
        current : `float`, optional
            Maximum setpoint current of the instrument (the default maximum
            current, by default).
        """
        if current is None:
            current = self.max_current
        self.instrument.write('OUTPUT:LIMIT:CURRENT {0:.3f}'.format(current))

    def read_output(self): # check return type (str or bool)
        """Read the output state of the instrument.

        Returns
        -------
        state : {'ON', 'OFF'}
            Output state of the instrument.

        Raises
        ------
        JVisaException
            Raised if an unknown response string is encountered.
        """
        state = str(self.instrument.queryString('OUTPUT?'))
        if state not in {'ON', 'OFF'}:
            raise JVisaException("Unknown response string encountered: {0}".format(state))
        return state

    def write_output(self, state):
        """Write the output state of the instrument.

        Parameters
        ----------
        state : {'ON', 'OFF'}
            Output state of the instrument.

        Raises
        ------
        ValueError
            Raised if parameter ``state`` is an invalid value.
        """
        if state in ['ON', 'OFF']:
            self.instrument.write('OUTPUT {0}'.format(state))
        else:
            raise ValueError("Not a valid value: {0}".format(state))

    def write_all(self):
        """Write all default operating parameters to the instrument."""
        self.write_voltage()
        self.write_max_voltage()
        self.write_max_current()

class BK9130BDevice(PowerDevice):
    
    def __init__(self, devc_id, voltages):
        self.voltages = voltages
        super().__init__('B&K 9130B PS', devc_id, baud_rate=4800, write_terminator='\n')

    def initialize(self)
        super().initialize()
        self.set_remote()

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
    """Interface to a B&K model 1697B power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    voltage : `float`
        Default operating voltage of the instrument.
    """

    def __init__(self, devc_id, voltage):
        self._voltage = voltage
        super().__init__('B&K 1697B PS', devc_id, write_terminator='\n')

    @parameter
    def voltage(self):
        """Default operating voltage of the instrument.
        """
        return self._voltage

    def get_voltage(self):
        """Get the setpoint voltage of the instrument.

        Returns
        -------
        voltage : `float`
            Setpoint voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('VOLTAGE?').rstrip('V'))

    def read_voltage(self):
        """Read the output voltage of the instrument.

        Returns
        -------
        voltage : `float`
            Output voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('MEASURE:VOLTAGE?').rstrip('V'))
        return voltage

    def write_voltage(self, voltage=None):
        """Write the setpoint voltage to the instrument.

        Parameters
        ----------
        voltage : `float`, optional
            Setpoint voltage of the instrument (the default operating voltage,
            by default).
        """
        if voltage is None:
            voltage = self.voltage
        self.instrument.write('VOLTAGE {0:.2f}V'.format(voltage))

    def read_output(self):
        """Read the output state of the instrument.

        Returns
        -------
        state : {'ON', 'OFF'}
            Output state of the instrument.

        Raises
        ------
        JVisaException
            Raised if an unknown response string is encountered.
        """
        response = self.instrument.queryString('OUTPUT?')
        if response == '0':
            state = 'ON'
        elif response == '1':
            state = 'OFF'
        else:
            raise JVisaException("Unknown response string encountered: {0}".format(response))
        return state

    def write_output(self, state):
        """Write the output state of the instrument.

        Parameters
        ----------
        state : {'ON', 'OFF'}
            Output state of the instrument."

        Raises
        ------
        ValueError
            Raised if ``state`` is an invalid value.
        """
        if state == 'ON':
            self.instrument.write('OUTPUT 0')
        elif state == 'OFF':
            self.instrument.write('OUTPUT 1')
        else:
            raise ValueError("Not a valid value: {0}".format(state))
