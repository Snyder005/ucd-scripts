#!/usr/bin/env ccs-script
# To Do:
#  * Write a useful publish state function
from ccs.power import BK9184Device, BK9130BDevice, BK1697BDevice

from time import sleep

class UCDPower(object):

    def __init__(self):

        self.hvbias_device = BK9184Device('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.1.1:1.0-port0',
                                          50.0, 60.0, 0.001)
        self.power_devices = (BK9130BDevice('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.3:1.0-port0',
                                            [8.0, 12.0, 5.0]),
                              BK9130BDevice('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.2:1.0-port0',
                                            [15.0, 15.0, 5.0]),
                              BK1697BDevice('/dev/serial/by-path/pci-0000:00:14.0-usb-0:12.1.4:1.0', 38.0))
    def power_on(self):
        try:
            if not self.is_power_on():
                # Turn off voltages
                self.power_devices[0].write_voltages([0.0, 0.0, 0.0])
                self.power_devices[1].write_voltages([0.0, 0.0, 0.0])

                self.power_devices[0].write_outputs(['ON', 'ON', 'ON'])
                self.power_devices[1].write_outputs(['ON', 'ON', 'ON'])
                self.power_devices[2].write_output('OFF')

                # Turn on OTM, Digital, and Heater voltages
                self.power_devices[0].write_voltages([0.0, 12.0, 5.0])
                self.power_devices[1].write_voltages([0.0, 0.0, 5.0])
                sleep(20)

                # Turn on CLK High, CLK Low, and Analog voltages
                self.power_devices[0].write_voltages()
                self.power_devices[1].write_voltages()    
                sleep(20)

                # Turn on OD
                self.power_devices[2].write_voltage()
                self.power_devices[2].write_output('ON')
                sleep(2)
        finally:
            self.publish_state()

    def power_off(self):
        self.hvbias_off() # raises error if fails

        try:
            # Set OD to 0V, by turning off output since minimum is 1 V
            self.power_devices[2].write_output('OFF')
            sleep(20)

            # Set CLK High, CLK Low, and analog voltages to 0.
            self.power_devices[0].write_voltages([0.0, 12.0, 5.0]) # Set chan 1 to 0V
            self.power_devices[1].write_voltages([0.0, 0.0, 5.0])
            sleep(20)

            # Set OTM, Digital and Heater voltages to 0.
            self.power_devices[0].write_voltages([0.0, 0.0, 0.0])
            self.power_devices[1].write_voltages([0.0, 0.0, 0.0])

            # Turn off outputs
            self.power_devices[0].write_outputs(['OFF', 'OFF', 'OFF'])
            self.power_devices[1].write_outputs(['OFF', 'OFF', 'OFF'])
            sleep(4)
        finally:
            self.publish_state()

    def hvbias_on(self):
        if not self.is_power_on():
            return
        try: # power on hvbias
            self.hvbias_device.write_all()
            self.hvbias_device.write_output('ON')
        finally:
            self.publish_state()

    def hvbias_off(self):
        try:
            self.hvbias_device.write_output('OFF')
        finally:
            self.publish_state()

    def is_hvbias_on(self):
        return self.hvbias_device.read_output() == 'ON'

    def set_hvbias(self, voltage): # Option to set opVoltage and then write if on.
        try:
            self.hvbias_device.write_voltage(voltage)
        finally:
            self.publish_state()

    def publish_state(self):
        """Read state of power supplies and publish."""
        
        vnames = ['Analog', 'Heater', 'Digital', 'CLK Low', 'CLK High', 'OTM', 'OD', 'BSS']
        voltages = self.power_devices[0].read_voltages() + \
                   self.power_devices[1].read_voltages() + \
                   [self.power_devices[2].read_voltage()] + \
                   [self.hvbias_device.read_voltage()]
        
        for i, vname in enumerate(vnames):
            print("{0} = {1:.1f}".format(vname, voltages[i]))

    def is_power_on(self):

        is_on = True

        states = self.power_devices[0].read_outputs() + \
                 self.power_devices[1].read_outputs() + \
                 [self.power_devices[2].read_output()]

        for state in states:
            if state != 'ON':
                is_on = False
                break

        return is_on
