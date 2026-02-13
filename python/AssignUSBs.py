#!/usr/bin/env python
#USB ASSIGNING SCRIPT

# This script should be run after a system reset it assigns the correct USB adresses in /dev/ttyUSB? to the correct devices by querying them and returning the correct device.
#Daniel Polin 2023

import pyvisa 
import subprocess

###############################################################################
# Set the Baud rates. The jvisa default is 9600, but the BK Precision 9130Bs run at 4800
Baud9130B=	4800
Baud1697=	9600
Baud9184=	57600
###############################################################################
#Set termination characters where required
BK9130Btermination='\n'
BK1697termination='\r'
BK9184termination='\r\n'

###############################################################################
#Set the ID names of the devices
ID9130B1 = "B&K Precision, 9130B, 802361023737520053, 1.10-1.04"
ID9130B2 = "B&K Precision, 9130B, 802361023737520051, 1.10-1.04"
OK1697 = "OK"
ID9184 = "B&K PRECISION,9184,373B15105,2.04,0"

def main():

    BK9130B1address = 'WARNING: BK9130B1 not detected'
    BK9130B2address = 'WARNING: BK9130B2 not detected'
    BK1697address = 'WARNING: BK1697 not detected'
    BK9184address = 'WARNING: BK9184 not detected'
    shutteraddress = 'WARNING: Shutter not detected'
    stageaddress = 'Warning: Stage motor not detected'


    instrument_data = {}
    # Assign the shutter
    try:
        sh = subprocess.check_output(['ls', '-l', '/dev/shutter']).decode()
        shutter_address='ASRL1'+sh[-2]+'::INSTR'
    except Exception as e:
        print("Failure to write shutter address. Exception of type %s and args = \n"%type(e).__name__, e.args)
    else:
        instrument_data['Shutter'] = {'resource_name' : shutter_address}

    # Assign the stage
    try:
        sh = subprocess.check_output(['ls', '-l', '/dev/stage']).decode()
        stage_address='ASRL1'+sh[-2]+'::INSTR'
    except Exception as e:
        print("Failure to write stage motor address. Exception of type %s and args = \n"%type(e).__name__, e.args)
    else:
        instrument_data['Stage'] = {'resource_name' : stage_address}

    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    for tty in resources:
        device = rm.open_resource(tty)

        # Look for BK9130s
        if BK9130B1address == 'WARNING: BK9130B1 not detected' or BK9130B2address == 'WARNING: BK9130B2 not detected':        
            device.baud_rate = Baud9130B
            device.write_termination = BK9130Btermination
            device.read_termination = BK9130Btermination
            
            try:
                ID = device.query('*IDN?')
            except:
                pass
            else:
                if ID == ID9130B1:
                    BK9130B1address = tty
                    instrument_data['BK9130B1'] = {'resource_name' : tty}
                elif ID == ID9130B2:
                    BK9130B2address = tty
                    instrument_data['BK9130B2'] = {'resource_name' : tty}
                continue

        # Look for the BK9184
        if BK9184address == 'WARNING: BK9184 not detected':
            device.baud_rate = Baud9184
            device.read_termination = BK9184termination
            try:
                ID = device.query('*IDN?')
            except:
                pass
            else:
                if ID == ID9184:
                    BK9184address = tty
                    instrument_data['BK9184'] = {'resource_name' : tty}
                continue

        if BK1697address == 'WARNING: BK1697 not detected':
            device.baud_rate = Baud1697
            device.write_termination = BK1697termination
            device.read_termination = BK1697termination
            try:
                okresponse = device.query('\rSESS00')
            except:
                pass
            else:
                if okresponse == OK1697:
                    BK1697address = tty
                    instrument_data['BK1697'] = {'resource_name' : tty}
            continue

    # Print results
    print('BK9130B1: '+BK9130B1address)
    print('BK9130B2: '+BK9130B2address)
    print('BK9184: '+BK9184address)
    print('BK1697: '+BK1697address)
    print('Shutter: '+shutteraddress)
    print('Stage Motor: '+stageaddress)

    print(instrument_data)

if __name__ == '__main__':
    main()
