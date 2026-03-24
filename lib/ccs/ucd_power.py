#!/usr/bin/env ccs-script
# To Do:
#  * Write a useful publish state function
from ccs.power import BK9184Device, BK9130BDevice, BK1697BDevice
from ccs.power import PowerControl

from time import sleep

class UCDPower(object):

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
