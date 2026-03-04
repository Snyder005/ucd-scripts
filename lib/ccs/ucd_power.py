from xyz.froud.jvisa import JVisaResourceManager, JVisaException
from ccs.power import BK9130BDevice, BK9184Device, BK1697BDevice
     
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
