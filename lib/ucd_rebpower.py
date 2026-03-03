#!/usr/bin/env ccs-script
from xyz.froud.jvisa import JVisaResourceManager, JVisaException
# import Device

class PowerDevice(Device):

    def readIDN(self):
        """Read the identification string of the instrument.

        Returns
        -------
        idn : `str`
            Identification string of the instrument.
        """
        idn = self.instrument.queryString('*IDN?')
        return idn

    def isConnected(self):
        try:
            self.readIDN()
        except JVisaException:
            connected = False
        else:
            conncted = True

        return connected

    def writeOutput(self, state):
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

class BKPrecision9184(PowerDevice):

    def __init__(self, devcId, voltage, maxVoltage, maxCurrent):
        self.baudRate = 57600
        self.writeTerminator = '\r\n'
        self.setVoltage(voltage)
        self.setMaxVoltage(maxVoltage)
        self.setMaxCurrent(maxCurrent)

        super().__init__('B&K 9184 PS', devcId)
        self.initialize()

    def initialize(self)
        self().initialize()
        try:
            self.getIDN()
            self.setRemote()
        except JVisaException as e:
            self.close()
        else:
            raise e

    def setVoltage(self, voltage):
        """Set the operating voltage of the instrument.

        Parameters
        ----------
        voltage : `float`
            Operating voltage of the instrument in units of volts.
        """
        self._opVoltage = voltage

    def getVoltage(self):
        """Get the operating voltage of the instrument."""
        return self._opVoltage

    def readVoltage(self):
        """Read the output voltage of the instrument.
        
        Returns
        -------
        voltage : `float`
            Output voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('MEASURE:VOLTAGE?'))
        return voltage

    def writeVoltage(self):
        """Write the operating voltage to the instrument."""
        self.instrument.write('VOLTAGE {0:.3f}'.format(self._opVoltage))

    def readCurrent(self):
        """Read the output current of the instrument.

        Returns
        -------
        current : `float`
            Output current of the instrument.
        """
        current = float(self.instrument.queryString('MEASURE:CURRENT?'))
        return current

    def setMaxVoltage(self, maxVoltage):
        """Set the maximum operating voltage of the instrument.
    
        Parameters
        ----------
        maxVoltage : `float`
            Maximum operating voltage of the instrument.
        """
        self._opMaxVoltage = maxVoltage

    def getMaxVoltage(self):
        """Get the maximum operating voltage of the instrument."""
        return self._opMaxVoltage

    def readMaxVoltage(self):
        """Read the maximum operating voltage of the instrument.

        Returns
        -------
        maxVoltage : `float`
            Maximum operating voltage of the instrument.
        """
        maxVoltage = float(self.instrument.queryString('OUTPUT:LIMIT:VOLTAGE?'))
        return maxVoltage

    def writeMaxVoltage(self):
        """Write the maximum operating voltage to the instrument."""
        self.instrument.write('OUTPUT:LIMIT:VOLTAGE {0:.3f}'.format(self._opMaxVoltage))

    def setMaxCurrent(self, maxCurrent):
        """Set the maximum operating current of the instrument.

        Parameters
        ----------
        maxCurrent : `float`
            Maximum operating current of the instrument.
        """
        self._opMaxCurrent = maxCurrent

    def getMaxCurrent(self)
        """Get the maximum operating current of the instrument."""
        return self._opMaxCurrent

    def readMaxCurrent(self):
        """Read the maximum operating current of the instrument.

        Returns
        -------
        maxCurrent : `float`
            Maximum operating current of the instrument.
        """
        current = float(self.instrument.queryString('OUTPUT:LIMIT:CURRENT?'))

    def writeMaxCurrent(self):
        """Write the maximum operating current to the instrument."""
        self.instrument.write('OUTPUT:LIMIT:CURRENT {0:.3f}'.format(self._opMaxCurrent))

    def readOutput(self): # check return type (str or bool)
        """Read the output state of the instrument.

        Returns
        -------
        state : `bool`
            Output state of the instrument.
        """
        state = self.instrument.queryString('OUTPUT?')
        return state

    def writeAll(self):
        """Write all operating parameters to the instrument."""
        self.writeVoltage()
        self.writeMaxVoltage()
        self.writeMaxCurrent()

class BK9130BDevice(PowerDevice):
    
    def __init__(self, devcId, voltages):
        self.baudRate = 4800
        self.writeTerminator = '\n'
        self.setVoltages(voltages)

        super().__init__('B&K 9130B PS', devcId)
        self.initialize()

    def initialize(self)
        self().initialize()
        try:
            self.getIDN()
            self.setRemote()
        except JVisaException as e:
            self.close()
        else:
            raise e

    def setVoltages(self, voltages):
        """Set the operating voltages of the instrument.

        Parameters
        ----------
        voltages : `list` [`float`]
            Operating voltages of the instrument.
        """
        self._opVoltages = voltages

    def getVoltages(self):
        """Get the operating voltages of the instrument."""
        return self._opVoltages

    def readVoltages(self):
        """Read the output voltages of the instrument.

        Returns
        -------
        voltages : `list` [`float`]
            Output voltages of the instrument.
        """
        voltages = [float(v) for v in self.instrument.queryString('MEASURE:VOLTAGE:ALL?').split(',')]
        return voltages

    def writeVoltages(self):
        """Write the operating voltages to the instrument."""
        self.instrument.write('APPLY:VOLTAGE {0},{1},{2}'.format(*self._opVoltages))

    def readOutput(self): # check return type (str or bool)
        """Read the output state of the instrument.

        Returns
        -------
        state : `bool`
            Output state of the instrument.
        """
        state = self.instrument.queryString('OUTPUT:STATE?')
        return state

class BK1697BDevice(PowerDevice):

    def __init__(self, devcId, voltage):
        self.writeTerminator = '\n'
        self.setVoltage(voltage)

        super().__init__('B&K 1697B PS', devcId)
        self.initialize()

    def initialize(self)
        self().initialize()
        try:
            self.getIDN()
        except JVisaException as e:
            self.close()
        else:
            raise e

    def setVoltage(self, voltage):
        """Set the operating voltage of the instrument.
    
        Parameters
        ----------
        voltage : `float`
            Operating voltage of the instrument.
        """
        self.opVoltage = voltage

    def getVoltage(self):
        """Get the operating voltage of the instrument."""
        return self.opVoltage

    def readVoltage(self):
        """Read the output voltage of the instrument.

        Returns
        -------
        voltage : `float`
            Output voltage of the instrument.
        """
        voltage = float(self.instrument.queryString('VOLTAGE?'))
        return voltage

    def writeVoltage(self):
        """Write the operating voltage to the instrument."""
        self.instrument.write('VOLTAGE {0:.2f}'.format(self.opVoltage))

    def readOutput(self): # check return type
        """Read the output state of the instrument.

        Returns
        -------
        state : `bool`
            Output state of the instrument.
        """
        state = self.instrument.queryString('OUTPUT?')
        return state
      
class UCDPower(object):

    def check_connections() # Check connection to all power supplies

    def read_BSS()

    def read_volt() # Reads all power supply voltages

    def check_volt() # check difference between set values and actual values

    def check_for_off_volt() # check difference between 0V and actual values

    def bss_on_arbitrary_voltage() # Turn on BSS with new back bias voltage

class _UCDPower(object):
    
    pwrOnn = (None, None, None, None, None, None
    voltage_names = ("Digital", "Analog", "ClockHigh", "ClockLow", "OD", "HVBIAS", "OTM", "Heater")
    
    reb_voltage_names = ("Digital", "Analog", "ClockHigh", "ClockLow", "OD", "OTM", "Heater")

    pwrOn = {name : None for name in voltage_names}

    @classmethod
    def fromProperties(cls, properties_file):
        properties = Properties()
        with FileInputStream('instruments.properties') as f:
            properties.load(f)
    
        resource_names = (properties['bk9130b1/address'],
                          properties['bk9130b2/address'],
                          properties['bk1697/address'])
        return cls(resource_names)

    def powerOn(self):
        try:
            if not self.isPowerOn():
                pass
                # reb.powerOn()
                # reb.waitPowerOn(POWER_TIMEOUT)
        finally:
            self.updatePowerState()

    def powerOff(self):
        try:
            hvBias.writeOutput(False)
            pass
        except Exception as e:
            excp = e
        try:
            #reb.powerOff()
            #reb.waitPowerOff(POWER_TIMEOUT)
        finally:
            self.updatePowerState()

    def hvBiasOn(self):
        if not self.isPowerOn(): return
        try:
            hvBias.writeOutput(True)
        finally:
            self.updatePowerState()

    def hvBiasOff(self):
        try:
            hvBias.writeOutput(False)
        finally:
            self.updatePowerState()

    def isHvBiasOn(self):
        return self.powerOn['HVBias']

    def setHvBias(self, voltage):
        try:
            if self.powerOn['HVBias']:
                hvBias.writeVoltage(voltage)
        finally:
            # Update hv bias value
            pass

    def getFullState(self):
            # UCDPowerState(self.powerOn, hvBiasControl.getVoltage())
            # UCDPowerState looks like a subclass of dict with predefined keys with values set on __init__

    def updatePowerState(self):

        states = self.bk9130b_1.readOutputs()
        self.powerOn['Analog'] = states[0]
        self.powerOn['Heater'] = states[1]
        self.powerOn['Digital'] = states[2]

        states = self.bk9130b_2.readOutputs()
        self.powerOn['ClockLow'] = states[0]
        self.powerOn['ClockHigh'] = states[1]
        self.powerOn['OTM'] = states[2]

        state = self.bk1697.readOutput()
        self.powerOn['OD'] = state    

        state = self.hvBias.readOutput()
        self.powerOn['HBVias'] = state

    def isPowerOn(self):

        for name in reb_voltage_name:
            if not self.powerOn[name]:
                return False
        return True

    def _powerOn(self):
    
        # check if voltages are on

        # if voltages in unknown state turn them off

        # set bk9130 voltages to 0V and set to on
        self.bk9130b_1.setVoltages((0, 0, 0))
        self.bk9130b_2.setVoltages((0, 0, 0))

        # set bk9130b to on, set 1697 to off
        self.bk9130b_1.setOutputState(True)
        self.bk9130b_2.setOutputState(True)
        self.bk1697.setOutputState(False)

        # set otm, digital, and heater voltages
        self.bk9130b_1.setVoltages((0, VP_HTR, VP5))
        self.bk9130b_2.setVoltages((0, 0, V_OTM))
        time.sleep(SETTLE_TIME)

        # set clock voltages
        self.bk9130b_1.setVoltages((VP7, VP_HTR, VP5))
        self.bk9130b_2.setVoltages((VP15, VN15, V_OTM))
        self.bk1697.setVoltage(VP40)
        time.sleep(SETTLE_TIME)

        # set bk1697 to on
        self.bk1697.setOutputState(True)

    def _powerOff(self):

        # check if voltages are off; if not, proceed.
    
        # set bk1697 to off.
        self.bk1697.setOutputState(False)

        # set clock voltages and analog to 0V
        self.bk9130b_1.setVoltages((0, voltages[1], voltages[2]))
        self.bk9130b_2.setVoltages((0, 0, voltages[3]))
        time.sleep(SETTLE_TIME)

        # set otm, digital, and heater voltages to 9V
        self.bk9130b_1.setVoltages((0, 0, 0))
        self.bk9130b_2.setVoltages((0, 0, 0))

        # bk9130b set to off
        self.bk9130b_1.setOutputState(False)
        self.bk9130b_2.setOutputState(False)
