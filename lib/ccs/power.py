#!/usr/bin/env ccs-script
from ccs.device import SerialDevice

__all__ = ['BK9130BDevice', 'BK9184Device', 'BK1697BDevice']

class PowerDevice(SerialDevice):

    def read_idn(self):
        """Read the identification string of the power supply.

        Returns
        -------
        idn : `str`
            Identification string of the power supply.
        """
        idn = self.query('*IDN?') # Throws any exceptions from read/write
        return idn

    def is_connected(self):
        """Check if the power supply is connected.

        Returns
        -------
        connected : `bool`
            `True` if the power supply is connected. `False` if not.
        """
        if not super(PowerDevice, self).is_connected():
            return False
        try:
            idn = self.read_idn() # Must throw an exception
        except:
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
        Default operating voltage of the power supply.
    max_voltage : `float`
        Default maximum voltage of the power supply.
    max_current : `float`
        Default maximum current of the power supply.
    """

    def __init__(self, devc_id, voltage, max_voltage, max_current):
        self._voltage = voltage
        self._max_voltage = max_voltage
        self._max_current = max_current
        super(BK9184Device, self).__init__('B&K 9184 PS', devc_id, baud_rate=57600, 
                                           write_terminator='\r\n', read_terminator='\r\n')

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
        """Get the setpoint voltage of the power supply.

        Returns
        -------
        voltage : `float`
            Setpoint voltage of the power supply.
        """
        voltage = float(self.query('VOLT?'))
        return voltage

    def read_voltage(self):
        """Read the output voltage of the power supply.
        
        Returns
        -------
        voltage : `float`
            Output voltage of the power supply.
        """
        voltage = float(self.query('MEAS:VOLT?'))
        return voltage

    def write_voltage(self, voltage=None):
        """Write the setpoint voltage to the power supply.

        Parameters
        ----------
        voltage : `float`
            Setpoint voltage of the power supply (the default operating 
            voltage, by default)
        """
        if voltage is None:
            voltage = self.voltage
        self.write('VOLT {0:.3f}'.format(voltage))

    def read_current(self):
        """Read the output current of the supply.

        Returns
        -------
        current : `float`
            Output current of the power supply.
        """
        current = float(self.query('MEAS:CURR?'))
        return current

    def read_max_voltage(self):
        """Read the maximum operating voltage of the power supply.

        Returns
        -------
        max_voltage : `float`
            Maximum operating voltage of the power supply.
        """
        max_voltage = float(self.query('OUT:LIM:VOLT?'))
        return max_voltage

    def write_max_voltage(self, voltage=None):
        """Write the maximum setpoint voltage to the power supply.

        Parameters
        ----------
        voltage : `float`, optional
            Maximum setpoint voltage of the power supply (the default maximum
            voltage, by default).
        """
        if voltage is None:
            voltage = self.max_voltage
        self.write('OUT:LIM:VOLT {0:.3f}'.format(voltage))

    def read_max_current(self):
        """Read the maximum operating current of the power supply.

        Returns
        -------
        max_current : `float`
            Maximum operating current of the power supply.
        """
        max_current = float(self.query('OUT:LIM:CURR?'))
        return max_current

    def write_max_current(self, current=None):
        """Write the maximum setpoint current to the power supply.

        Parameters
        ----------
        current : `float`, optional
            Maximum setpoint current of the power supply (the default maximum
            current, by default).
        """
        if current is None:
            current = self.max_current
        self.write('OUT:LIM:CURR {0:.3f}'.format(current))

    def read_output(self): # check return type (str or bool)
        """Read the output state of the power supply.

        Returns
        -------
        state : {'ON', 'OFF'}
            Output state of the power supply.

        Raises
        ------
        JVisaException
            Raised if an unknown response string is encountered.
        """
        state = self.query('OUT?')
        if state not in {'ON', 'OFF'}:
            raise IOError("Unknown response string encountered: {0}".format(state))
        return state

    def write_output(self, state):
        """Write the output state of the power supply.

        Parameters
        ----------
        state : {'ON', 'OFF'}
            Output state of the supply.

        Raises
        ------
        ValueError
            Raised if parameter ``state`` is an invalid value.
        """
        if state in ['ON', 'OFF']:
            self.write('OUT {0}'.format(state))
        else:
            raise ValueError("Not a valid value: {0}".format(state))

    def write_all(self):
        self.write_voltage()
        self.write_max_voltage()
        self.write_max_current()

class BK9130BDevice(PowerDevice):
    """Interface to a B&K model 9130B power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    voltages : `list` [`float`]
        Default operating voltages of the power supply channels.
    """
    
    def __init__(self, devc_id, voltages):
        self._voltages = voltages # check that three provided
        super(BK9130BDevice, self).__init__('B&K 9130B PS', devc_id, baud_rate=4800, 
                                            write_terminator='\n', read_terminator='\n')

    @property
    def voltages(self):
        """Default operating voltages (`list` [`float`]).
        """
        return self._voltages

    def get_voltage(self, channel):
        """Get setpoint voltage of a power supply channel.

        Parameters
        ----------
        channel : `int`
            Power supply channel number.
        
        Returns
        -------
        voltage : `float`
            Setpoint voltage of the power supply channel.

        Raises
        ------
        JVisaException
            Raised if ``channel`` is an invalid channel number.
        """
        self.select_channel(channel)
        voltage = float(self.query('VOLT?'))
        return voltage
    
    def read_voltage(self, channel):
        """Read the output voltage of a power supply channel.

        Parameters
        ----------
        channel : `int`
            Power supply channel number.

        Returns
        -------
        voltage : `float`
            Output voltage of the power supply channel.

        Raises
        ------
        JVisaException
            Raised if ``channel`` is an invalid channel number.
        """
        self.select_channel(channel)
        voltage = float(self.query('MEAS:VOLT?'))
        return voltage

    def write_voltage(self, channel, voltage=None):
        """Write the setpoint voltage to a power supply channel.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.
        voltage : `float`
            Setpoint voltage of the power supply channel (the default 
            operating voltage, by default).
    
        Raises
        ------
        JVisaException
            Raised if ``channel`` is an invalid channel number.
        """
        self.select_channel(channel)
        if voltage is None:
            voltage = self.voltages[chan-1]
        self.write('VOLT {0:.1f}'.format(voltage))
        
    def get_voltages(self):
        """Get the setpoint voltages of the power supply channels.

        Returns
        -------
        voltages : `list` [`float`]
            Setpoint voltages of the power supply channels.
        """
        voltages = [float(res) for res in self.query('APP:VOLT?').split(',')]
        return voltages

    def read_voltages(self):
        """Read the output voltages of the power supply channels.

        Returns
        -------
        voltages : `list` [`float`]
            Output voltages of the power supply channels.
        """
        voltages = [float(res) for res in self.query('MEAS:VOLT:ALL?').split(',')]
        return voltages

    def write_voltages(self, voltages=None):
        """Write the setpoint voltages to the power supply channels.

        Parameters
        ----------
        voltages : `list` [`float`], optional
            Setpoint voltages of the power supply channels (the default 
            operating voltages, by default).
        """
        if voltages is None:
            voltages = self.voltages
        self.write('APP:VOLT {0:.1f},{1:.1f},{2:.1f}'.format(*voltages))

    def read_output(self, channel):
        """Read the output state of the power supply channel.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.

        Returns
        -------
        state : {'ON', 'OFF'}
            Output state of the power supply channel.

        Raises
        ------
        JVisaException
            Raised if ``channel`` is an invalid channel number or an unknown
            response string is encountered.
        """
        self.select_channel(channel)
        response = self.query('CHAN:OUTP?')
        if response == '0':
            state = 'OFF'
        elif response == '1':
            state = 'ON'
        else:
            raise IOError("Unknown response string encountered: {0}".format(response))
        return state

    def write_output(self, channel, state):
        """Write the output state of the power supply.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.
        state : {'ON', 'OFF'}
            Output state of the power supply channel."

        Raises
        ------
        JVisaException
            Raised if ``channel`` is an invalid channel number.
        ValueError
            Raised if ``state`` is an invalid value.
        """
        self.select_channel(channel)
        if state == 'ON':
            self.write('CHAN:OUTP 1')
        elif state == 'OFF':
            self.write('CHAN:OUTP 0')
        else:
            raise ValueError("Not a valid value: {0}".format(state))

    def read_outputs(self):
        """Read output states of the power supply channels.

        Returns
        -------
        states : `list` [{'ON', 'OFF'}]
            Output states of the power supply channels.
    
        Raises
        ------
        JVisaException
            Raised if an unknown response string is encountered.
        """
        responses = [res.lstrip() for res in self.query('APP:OUT?').split(',')]
        states = []
        for response in responses:
            if response == '0':
                states.append('OFF')
            elif response == '1':
                states.append('ON')
            else:
                raise IOError("Unknown response string encountered: {0}".format(response))
        return states

    def write_outputs(self, states):
        """Write output states to the power supply channels.

        Parameters
        ----------
        states : `list` [{'ON', 'OFF'}]
            Output states of the power supply channels.

        Raises
        ------
        ValueError
            Raised if ``states`` contains an invalid value.
        """
        outputs = []
        for state in states:
            if state == 'ON':
                outputs.append('0')
            elif state == 'OFF':
                outputs.append('1')
            else:
                raise ValueError("Not a valid value: {0}".format(state))
        self.write('APP:OUT {0},{1},{2}'.format(*outputs))
        
    def select_channel(self, channel):
        """Select the power supply channel.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.

        Raises
        ------
        JVisaException
            Raised if ``channel`` is an invalid channel number.
        """
        if channel not in [1, 2, 3]:
            raise IOError("Invalid channel number: {0}".format(channel))
        self.write('INST:NSEL {0}'.format(channel))

    def read_channel(self, channel):
        channel = int(self.query('INST:NSEL?'))
        return channel

class BK1697BDevice(PowerDevice):
    """Interface to a B&K model 1697B power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    voltage : `float`
        Default operating voltage of the power supply.
    """

    def __init__(self, devc_id, voltage):
        self._voltage = voltage
        super(BK1697BDevice, self).__init__('B&K 1697B PS', devc_id, baud_rate=9600, 
                                            write_terminator='\n', read_terminator='\r\n')

    @property
    def voltage(self):
        """Default operating voltage (`float`).
        """
        return self._voltage

    def get_voltage(self):
        """Get the setpoint voltage of the power supply.

        Returns
        -------
        voltage : `float`
            Setpoint voltage of the power supply.
        """
        voltage = float(self.query('VOLTAGE?').rstrip('V'))
        return voltage

    def read_voltage(self):
        """Read the output voltage of the power supply.

        Returns
        -------
        voltage : `float`
            Output voltage of the power supply.
        """
        voltage = float(self.query('MEASURE:VOLTAGE?').rstrip('V'))
        return voltage

    def write_voltage(self, voltage=None):
        """Write the setpoint voltage to the power supply.

        Parameters
        ----------
        voltage : `float`, optional
            Setpoint voltage of the power supply (the default operating 
            voltage, by default).
        """
        if voltage is None:
            voltage = self.voltage
        self.write('VOLTAGE {0:.2f}V'.format(voltage))

    def read_output(self):
        """Read the output state of the power supply.

        Returns
        -------
        state : {'ON', 'OFF'}
            Output state of the power supply.

        Raises
        ------
        JVisaException
            Raised if an unknown response string is encountered.
        """
        response = self.query('OUTPUT?').rstrip('\r\n')
        if response == '0':
            state = 'ON'
        elif response == '1':
            state = 'OFF'
        else:
            raise IOError("Unknown response string encountered: {0}".format(response))
        return state

    def write_output(self, state):
        """Write the output state of the power supply.

        Parameters
        ----------
        state : {'ON', 'OFF'}
            Output state of the power supply."

        Raises
        ------
        ValueError
            Raised if ``state`` is an invalid value.
        """
        if state == 'ON':
            self.write('OUTPUT 0')
        elif state == 'OFF':
            self.write('OUTPUT 1')
        else:
            raise ValueError("Not a valid value: {0}".format(state))
