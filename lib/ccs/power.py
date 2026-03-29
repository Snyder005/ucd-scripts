#!/usr/bin/env ccs-script
# To Do:
# * Write init function for UCDPower to create from properties file.
# * Create state functions to handle printing channel states.
# * Error handling of PowerException and DeviceException (from SerialDevice)
# * (Optional) Add check for not connected to read/write/query.
#   Refuse all commands if not connected. Raise exception?
# * (Optional) Add ID check to initialize method
from ccs.device import SerialDevice
from ccs.data import PowerException
from ccs.data import DeviceException

class UCDPowerMain(object):

    def __init__(self):

        # Define devices
        self.bk9184 = BK9184Device('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.1.1:1.0-port0')
        self.bk9130b1 = BK9130BDevice('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.3:1.0-port0')
        self.bk9130b2 = BK9130BDevice('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.2:1.0-port0')
        self.bk1697b = BK1697BDevice('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.1.4:1.0')

        # Define controls
        self.reb_controls = {'Analog' : PowerControl('Analog', self.bk9130b1, 1, 8.0, 0.75),
                             'Heater' : PowerControl('Heater', self.bk9130b1, 2, 12.0, 1.0),
                             'Digital' : PowerControl('Digital', self.bk9130b1, 3, 5.0, 1.5),
                             'ClockLow' : PowerControl('ClockLow', self.bk9130b2, 1, 15.0, 0.1),
                             'ClockHigh' : PowerControl('ClockHigh', self.bk9130b2, 2, 15.0, 0.1),
                             'OD' : PowerControl('OD', self.bk1697b, 0, 38.0, 0.05)}

        self.hvbias_control = PowerControl('HVBias', self.bk9184, 0, 50.0, 0.001)
        self.otm_control = PowerControl('OTM', self.bk9130b2, 3, 5.0, 0.5)

    def power_on(self):

        try:
            if not self.is_power_on():
                
                # Turn on OTM, Digital, and Heater voltages
                self.reb_controls['Digital'].power_on()
                self.reb_controls['Heater'].power_on()
                sleep(20)

                # Turn on Clk High, Clk Low, and Analog voltages
                self.reb_controls['ClockHigh'].power_on()
                self.reb_controls['ClockLow'].power_on()
                self.reb_controls['Analog'].power_on()
                sleep(20)

                # Turn on OD
                self.reb_controls['OD'].power_on()
                sleep(2)
        finally:
            self.publish_state()

    def power_off(self):
        self.hvbias_off() # raises error if fails

        try:
            self.reb_controls['OD'].power_off()
            sleep(20)

            self.reb_controls['Analog'].power_off()
            self.reb_controls['ClockLow'].power_off()
            self.reb_controls['ClockHigh'].power_off()
            sleep(20)
    
            self.reb_controls['Heater'].power_off()
            self.reb_controls['Digital'].power_off()
            sleep(4)
        finally:
            self.publish_state()
           
    def hvbias_on(self):
        if not self.is_power_on():
            return
        try:
            self.hvbias_control.write_voltage()
            self.hvbias_control.write_current()
            self.hvbias_control.write_output('ON')
        finally:
            self.publish_state()

    def hvbias_off(self):
        try:
            self.hvbias_control.write_output('OFF')
        finally:
            self.publish_state()

    def is_hvbias_on(self):
        return self.hvbias_control.read_output() == 'ON'

    def set_hvbias(self, voltage):
        self.hvbias_control.op_voltage = voltage
        try:
            if self.is_hvbias_on:
                self.hvbias_control.write_voltage()
        finally:
            self.publish_state()

    def otm_on(self):
        try:
            self.otm_control.power_on()
        finally:
            self.publish_state()

    def otm_off(self):
        try:
            self.otm_control.power_off()
        finally:
            self.publish_state()

    def publish_state(self):
        """Read state of power supplies and publish."""
        
        # REB control
        for control in self.reb_controls.values():
            name, state, voltage, current = control.get_state()
            print('{0}: State = {1}, voltage = {2:.3f} V, current = {3:.3f} A'.format(name, state, voltage, current))

        # HVBias control
        name, state, voltage, current = self.hvbias_control.get_state()
        print('{0}: State = {1}, voltage = {2:.3f} V, current = {3:.3f} A'.format(name, state, voltage, current))

        # OTM control
        name, state, voltage, current = self.otm_control.get_state()
        print('{0}: State = {1}, voltage = {2:.3f} V, current = {3:.3f} A'.format(name, state, voltage, current))

    def is_power_on(self):

        is_on = True

        for control in self.reb_controls.values():
            state = control.read_output()
            if state != 'ON':
                is_on = False
                break

        return is_on

class PowerControl(object):
    """Power supply channel controller.

    Parameters
    ----------
    name : `str`
        Power supply channel name.
    devc : `PowerDevice`
        A power supply device interface.
    hw_chan : `int`
        Power supply channel number.
    op_voltage : `float`
        Power supply channel operating voltage.
    op_current : `float`, optional
        Power supply channel operating current.

    Raises
    ------
    PowerException
        Raised if the hardware channel number is invalid.
    """

    def __init__(self, name, devc, hw_chan, op_voltage, op_current):
        self.name = name
        self.devc = devc
        if (hw_chan < self.devc.MIN_CHAN) or (hw_chan > self.devc.MAX_CHAN):
            raise PowerException('HW channel number is invalid: {0}'.format(hw_chan))
        else:
            self.hw_chan = hw_chan
        self.op_voltage = op_voltage
        self.op_current = op_current

    def get_state(self):
        """Get state of the power supply channel."""
        try:
            state = self.read_output()
            voltage = 0.0 if state == 'NC' else self.read_voltage()
            current = 0.0 if state == 'NC' else self.read_current()
        except PowerException:
            state = 'NC'
            voltage = 0.0
            current = 0.0

        return self.name, state, voltage, current

    def read_voltage(self):
        """Read the power supply channel voltage.

        Returns
        -------
        voltage : `float`
            Power supply channel voltage.
        """
        return self.devc.read_voltage(self.hw_chan)

    def write_voltage(self):
        """Write the power supply channel setpoint voltage."""
        self.devc.write_voltage(self.op_voltage, self.hw_chan)
    
    def read_current(self):
        """Read the power supply channel current.

        Returns
        -------
        current : `float`
            Power supply channel current.
        """
        return self.devc.read_current(self.hw_chan)

    def write_current(self):
        """Write the power supply channel current limit."""
        self.devc.write_current(self.op_current, self.hw_chan)

    def read_output(self):
        """Read the power supply channel output.

        Returns
        -------
        state : {'NC', 'ON', 'OFF'}
            Power supply channel output state.
        """
        return self.devc.read_output(self.hw_chan)

    def write_output(self, state):
        self.devc.write_output(state, self.hw_chan)

    def power_on(self):
        self.write_voltage()
        self.write_current()
        self.write_output('ON')

    def power_off(self):
        self.write_output('OFF')

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

    MIN_CHAN = 0
    MAX_CHAN = 0

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

    MIN_CHAN = 0
    MAX_CHAN = 0

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
            raise PowerException
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
            raise PowerException("Not a valid value: {0}".format(state))

class BK9130BDevice(PowerDevice):
    """Interface to a B&K model 9130B power supply device.

    Parameters
    ----------
    devc_id : `str`
        Device resource name.
    """
    
    MIN_CHAN = 1
    MAX_CHAN = 3

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
        self.write_select(channel)
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
        self.write_select(channel)
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
        self.write_select(channel)
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
        self.write_select(channel)
        current = float(self.query('CURR?'))
        return current

    def get_currents(self):
        currents = [float(res) for res in self.query('APP:CURR?').split(',')]
        return currents

    def read_current(self, channel):
        self.write_select(channel)
        current = float(self.query('MEAS:CURR?'))
        return current

    def read_currents(self):
        currents = [float(res) for res in self.query('MEAS:CURR:ALL?').split(',')]
        return currents

    def write_current(self, current, channel):
        self.write_select(channel)
        self.write('CURR {0:.3f}'.format(current))

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

        self.write_select(channel)
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
        self.write_select(channel)
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
