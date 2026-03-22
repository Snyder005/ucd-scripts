#!/usr/bin/env ccs-script
# To Do:
# * (Optional) Add check for not connected to read/write/query.
#   Refuse all commands if not connected. Raise exception?
# * (Optional) Add ID check to initialize method
from ccs.device import SerialDevice
from ccs.data import PowerException
from ccs.data import DeviceException

__all__ = ['BK9130BDevice', 'BK9184Device', 'BK1697BDevice']

class PowerDevice(SerialDevice):

    def is_connected(self):
        """Check if the power supply is connected.

        All SerialDevice instances check if the connection to the serial port
        is open. PowerDevice and child class instances also verify successful
        read/write operations by querying for the device ID.

        Returns
        -------
        connected : `bool`
            `True` if the power supply is connected. `False` if not.
        """
        if not super(PowerDevice, self).is_connected():
            return False
        try:
            idn = self.get_idn() # Must throw an exception
        except:
            return False
        else:
            return True

    def get_idn(self):
        """Get the identification string of the power supply.

        Returns
        -------
        idn : `str`
            Identification string of the power supply.

        Raises
        ------
        DeviceException
            Raised if unable to read identification string.
        """
        idn = self.query('*IDN?')
        return idn

    # Override
    def _query(self, cmd, num_bytes=1024):
        try:
            super(PowerDevice, self).query(cmd, num_bytes=num_bytes, use_read_terminator=use_read_terminator)
        except DeviceException:
            raise PowerException

    # Override
    def _write(self):
        try:
            super(PowerDevice, self).write(cmd)
        except DeviceException:
            raise PowerException

class BK1697BDevice(PowerDevice):
    """Interface to a B&K model 1697B power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    """

    def __init__(self, devc_id):
        super(BK1697BDevice, self).__init__('B&K 1697B PS', devc_id, baud_rate=9600, 
                                            write_terminator='\n', read_terminator='\r\n')

    def get_voltage(self, channel=None):
        """Get the setpoint voltage of the power supply.

        Returns
        -------
        voltage : `float`
            Setpoint voltage of the power supply.
        """
        voltage = float(self.query('VOLTAGE?').rstrip('V'))
        return voltage

    def read_voltage(self, channel=None):
        """Read the output voltage of the power supply.

        Returns
        -------
        voltage : `float`
            Output voltage of the power supply.
        """
        voltage = float(self.query('MEASURE:VOLTAGE?').rstrip('V'))
        return voltage

    def write_voltage(self, voltage, channel=None):
        """Write the setpoint voltage to the power supply.

        Parameters
        ----------
        voltage : `float`, optional
            Setpoint voltage of the power supply.
        """
        self.write('VOLTAGE {0:.2f}V'.format(voltage))

    def get_current(self, channel=None):
        current = float(self.query('CURRENT?').rstrip('A'))
        return current

    def read_current(self, channel=None):
        current = float(self.query('MEASURE:CURRENT?').rstrip('A'))
        return current

    def write_current(self, current, channel=None):
        self.write('CURRENT {0:.2f}A'.format(current))

    def read_output(self, channel=None):
        """Read the output state of the power supply.

        Returns
        -------
        state : {'ON', 'OFF', 'NC'}
            Output state of the power supply.

        Raises
        ------
        PowerException
            Raised if an unknown response string is encountered.
        """
        if not self.is_connected():
            return 'NC'

        response = self.query('OUTPUT?').rstrip('\r\n')
        if response == '0':
            return 'ON'
        elif response == '1':
            return 'OFF'
        else:
            raise PowerException("Unknown response string encountered: {0}".format(response))
        return state

    def write_output(self, state, channel=None):
        """Write the output state of the power supply.

        Parameters
        ----------
        state : {'ON', 'OFF'}
            Output state of the power supply."

        Raises
        ------
        PowerException
            Raised if ``state`` is an invalid value.
        """
        if state == 'ON':
            self.write('OUTPUT 0')
        elif state == 'OFF':
            self.write('OUTPUT 1')
        else:
            raise PowerException("Not a valid value: {0}".format(state))

class BK9184Device(PowerDevice):
    """Interface to a B&K model 9184 power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    max_voltage : `float`
        Default maximum voltage of the power supply.
    max_current : `float`
        Default maximum current of the power supply.
    """
    MAX_VOLTAGE = 60.0
    MAX_CURRENT = 0.001

    def __init__(self, devc_id):
        super(BK9184Device, self).__init__('B&K 9184 PS', devc_id, baud_rate=57600, 
                                           write_terminator='\r\n', read_terminator='\r\n')
   
    def get_voltage(self, channel=None):
        """Get the setpoint voltage of the power supply.

        Returns
        -------
        voltage : `float`
            Setpoint voltage of the power supply.
        """
        voltage = float(self.query('VOLT?'))
        return voltage

    def read_voltage(self, channel=None):
        """Read the output voltage of the power supply.
        
        Returns
        -------
        voltage : `float`
            Output voltage of the power supply.
        """
        voltage = float(self.query('MEAS:VOLT?'))
        return voltage

    def write_voltage(self, voltage, channel=None):
        """Write the setpoint voltage to the power supply.

        Parameters
        ----------
        voltage : `float`
            Setpoint voltage of the power supply (the default operating 
            voltage, by default)
        """
        if voltage > self.MAX_VOLTAGE: # check to protect CCD
            raise DeviceException
        self.write('VOLT {0:.3f}'.format(voltage))

    def get_current(self, channel=None):
        current = float(self.query('CURR?'))
        return current

    def read_current(self, channel=None):
        """Read the output current of the supply.

        Returns
        -------
        current : `float`
            Output current of the power supply.
        """
        current = float(self.query('MEAS:CURR?'))
        return current

    def write_current(self, current, channel=None):
        self.write('CURR {0:.3f}'.format(current))

    def read_output(self, channel=None):
        """Read the output state of the power supply.

        Returns
        -------
        state : {'ON', 'OFF', 'NC'}
            Output state of the power supply.

        Raises
        ------
        PowerException
            Raised if an unknown response string is encountered.
        """
        if not self.is_connected():
            return 'NC'

        state = self.query('OUT?')
        if state not in {'ON', 'OFF'}:
            raise PowerException("Unknown response string encountered: {0}".format(state))
        return state

    def write_output(self, state, channel=None):
        """Write the output state of the power supply.

        Parameters
        ----------
        state : {'ON', 'OFF'}
            Output state of the supply.

        Raises
        ------
        PowerException
            Raised if parameter ``state`` is an invalid value.
        """
        if state in ['ON', 'OFF']:
            self.write('OUT {0}'.format(state))
        else:
            raise ValueError("Not a valid value: {0}".format(state))

class BK9130BDevice(PowerDevice):
    """Interface to a B&K model 9130B power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    """
    
    def __init__(self, devc_id):
        super(BK9130BDevice, self).__init__('B&K 9130B PS', devc_id, baud_rate=4800, 
                                            write_terminator='\n', read_terminator='\n')

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
        PowerException
            Raised if ``channel`` is an invalid channel number.
        """
        self.select_channel(channel)
        voltage = float(self.query('VOLT?'))
        return voltage

    def get_voltages(self):
        """Get the setpoint voltages of the power supply channels.

        Returns
        -------
        voltages : `list` [`float`]
            Setpoint voltages of the power supply channels.
        """
        voltages = [float(res) for res in self.query('APP:VOLT?').split(',')]
        return voltages
   
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
        PowerException
            Raised if ``channel`` is an invalid channel number.
        """
        self.select_channel(channel)
        voltage = float(self.query('MEAS:VOLT?'))
        return voltage

    def read_voltages(self):
        """Read the output voltages of the power supply channels.

        Returns
        -------
        voltages : `list` [`float`]
            Output voltages of the power supply channels.
        """
        voltages = [float(res) for res in self.query('MEAS:VOLT:ALL?').split(',')]
        return voltages

    def write_voltage(self, voltage, channel):
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
        PowerException
            Raised if ``channel`` is an invalid channel number.
        """
        self.select_channel(channel)
        self.write('VOLT {0:.3f}'.format(voltage))

    def write_voltages(self, voltages):
        """Write the setpoint voltages to the power supply channels.

        Parameters
        ----------
        voltages : `list` [`float`], optional
            Setpoint voltages of the power supply channels (the default 
            operating voltages, by default).
        """
        self.write('APP:VOLT {0:.3f},{1:.3f},{2:.3f}'.format(*voltages))
       
    def get_current(self, channel):
        self.select_channel(channel)
        current = float(self.query('CURR?'))
        return current

    def get_currents(self):
        currents = [float(res) for res in self.query('APP:CURR?').split(',')]
        return currents

    def read_current(self, channel):
        self.select_channel(channel)
        current = float(self.query('MEAS:CURR?'))
        return current

    def read_currents(self):
        currents = [float(res) for res in self.query('MEAS:CURR:ALL?').split(',')]
        return currents

    def write_current(self, current, channel):
        self.select_channel(channel)
        self.write('CURR {0:.3f}'.format(current)

    def write_currents(self, currents):
        self.write('APP:CURR {0:.3f},{1:.3f},{2:.3f}'.format(*currents))

    def read_output(self, channel):
        """Read the output state of the power supply channel.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.

        Returns
        -------
        state : {'ON', 'OFF', 'NC'}
            Output state of the power supply channel.

        Raises
        ------
        PowerException
            Raised if ``channel`` is an invalid channel number or an unknown
            response string is encountered.
        """
        if not self.is_connected():
            return 'NC'

        self.select_channel(channel)
        response = self.query('CHAN:OUTP?')
        if response == '0':
            state = 'OFF'
        elif response == '1':
            state = 'ON'
        else:
            raise PowerException("Unknown response string encountered: {0}".format(response))
        return state

    def read_outputs(self):
        """Read output states of the power supply channels.

        Returns
        -------
        states : `list` [{'ON', 'OFF', 'NC'}]
            Output states of the power supply channels.
    
        Raises
        ------
        PowerException
            Raised if an unknown response string is encountered.
        """
        if not self.is_connected():
            return ['NC', 'NC', 'NC']

        responses = [res.lstrip() for res in self.query('APP:OUT?').split(',')]
        states = []
        for response in responses:
            if response == '0':
                states.append('OFF')
            elif response == '1':
                states.append('ON')
            else:
                raise PowerException("Unknown response string encountered: {0}".format(response))
        return states

    def write_output(self, state, channel):
        """Write the output state of the power supply channel.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.
        state : {'ON', 'OFF'}
            Output state of the power supply channel."

        Raises
        ------
        PowerException
            Raised if ``channel`` is an invalid channel number or if ``state``
            is an invalid value.
        """
        self.select_channel(channel)
        if state == 'ON':
            self.write('CHAN:OUTP 1')
        elif state == 'OFF':
            self.write('CHAN:OUTP 0')
        else:
            raise PowerException("Not a valid value: {0}".format(state))

    def write_outputs(self, states):
        """Write output states to the power supply channels.

        Parameters
        ----------
        states : `list` [{'ON', 'OFF'}]
            Output states of the power supply channels.

        Raises
        ------
        PowerException
            Raised if ``states`` contains an invalid value.
        """
        outputs = []
        for state in states:
            if state == 'ON':
                outputs.append('1')
            elif state == 'OFF':
                outputs.append('0')
            else:
                raise PowerException("Not a valid value: {0}".format(state))

        self.write('APP:OUT {0},{1},{2}'.format(*outputs))        

    def write_select(self, channel):
        """Select the power supply channel.

        Parameters
        ----------
        channel : {1, 2, 3}
            Power supply channel number.

        Raises
        ------
        PowerException
            Raised if ``channel`` is an invalid channel number.
        """
        if channel not in [1, 2, 3]:
            raise PowerException("Invalid channel number: {0}".format(channel))
        self.write('INST:NSEL {0}'.format(channel))

    def read_select(self):
        """Read the power supply channel number.
        
        Returns
        -------
        channel : {1, 2, 3}
            Power supply channel number.
        """
        channel = int(self.query('INST:NSEL?'))
        return channel
