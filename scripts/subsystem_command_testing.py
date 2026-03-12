#!/usr/bin/env ccs-script
# This is used to test functions before adding to Jython subsystem

# Testing power off
from ccs.power import BK9184Device, BK9130BDevice, PowerDevice

from time import sleep

def hvbias_off():

    hvbias_device = BK9184Device('ttyUSB2', 50.0, 60.0, 0.001)

    hvbias_device.write_voltage(0.0)
    hvbias_device.write_output('OFF')

def command():
    # Before testing verify correct bk9130b assignments
    bk1697 = PowerDevice('BK 1697 PS', 'ttyUSB5', baud_rate=9600, 
                         write_terminator='\r', read_terminator='\r')
    bk9130b1 = BK9130BDevice('ttyUSB3', [8.0, 12.0, 5.0])
    bk9130b2 = BK9130BDevice('ttyUSB1', [15.0, 15.0, 5.0])

    print('BK9130B_1: ', bk9130b1.read_voltages())
    print('BK9130B_2: ', bk9130b2.read_voltages())

    return
    # check if reb voltages are off, return
    # else

    # Turn back bias off (does this matter if hvbias is already off?)
    hvbias_off()
    
    # Set OD to 0V
    bk1697.query('SOUT001')
    # wait a delay
    sleep(20)

    # Set clk high, clk low, and analog voltages to 0.
    bk9130b2.write_voltages([0.0, 0.0, None]) # Set chan 1/2 to 0V
    bk9130b1.write_voltages([0.0, None, None]) # Set chan 1 to 0V
    sleep(20)

    # Set OTM, digital, and heater, voltages to 0.
    bk9130b2.write_voltages([0.0, 0.0, 0.0])
    bk9130b1.write_voltages([0.0, 0.0, 0.0])

    bk9130b2.write_outputs(['OFF', 'OFF', 'OFF'])
    bk9130b1.write_outputs(['OFF', 'OFF', 'OFF'])
    sleep(4)

    # Check if reb voltages are off
    # if not off: Return

if __name__ == '__main__':
    hvbias_off()
