#!/usr/bin/env python

#Author: Daniel Polin
#Date: 2023

#This code interfaces and controls the x-y-z stage motor and the three linear encoders that read the stage position. This code is largely based and build on code written by Craig Lage for the same stage when it was controlled by the Storm system.

import time, fcntl, serial, struct

class Stage(object):
    def __init__(self):
        #*** XYZ stage stepper motor settings ***
        self.POS_NAME = ['x', 'y', 'z']
        self.STEPPER_NAME = ['I1M', 'I3M', 'I2M']
        self.stage_device_name='/dev/stage'
        
        #*** Encoder Settings ***
        # For optical encoders which read stage position
        # Various constants.  See /usr/local/src/pci_quad04/pci-quad04/RegMapPCI-QUAD04.pdf
        self.ENCODER_NAME = ['/dev/quad04/channel0_1', '/dev/quad04/channel0_3', '/dev/quad04/channel0_2'] # These are ordered (x, y, z)
        self.LOAD_CMD_REG = 0x7701 # Loads the command register
        self.X4  = 0x38 # Set Counter Mode Register (CMR). Selects Binary counting, Normal count mode, X4 scaling (readout in um)
        self.TRAN_PR_CNTR = 0x8 # Transfer PR register to 24 bit counter
        self.IOR_DISABLE_INDEX = 0x45 # Sets Input/Output Control register (IOR). Selects Load Cntr, A/B Enable gate, FLG1 Carry, FLG2 Borrow, 
        self.initialize_serial()
        self.initialize_encoders()
        return

    def initialize_serial(self):
        """Initializes the USB serial bus, using the python serial module
        
        returns: True is initialization is successful. False if not."""
        for NumTries in range(5):
            try:
                self.ser = serial.Serial(self.stage_device_name)
                self.ser.close()
                self.ser.open()
                return True
            except Exception as e:
                print("Failure initializing stage serial bus. Attempt number "+str(NumTries)+" Exception of type %s and args = \n"%type(e).__name__, e.args)    
                time.sleep(0.1)
                continue

        print("Failed to initialize Stage Serial Bus\n")
        return False

    def close_serial(self):
        """Closes the USB serial bus, using the python serial module
        
        returns: True if closed, False if not."""
        try:
            self.ser.close()
            return True
        except Exception as e:
            print("Failed to close Stage serial bus. Exception of type %s and args = \n"%type(e).__name__, e.args )   
            return False
    
    def initialize_encoders(self):
        """Initializes the optical encoders and sets the read positions to zeros.
        
        returns: True if successful, False if not."""
        for NumTries in range(5):
            try:
                self.fd_channel = []
                for i in range(3):
                    self.fd_channel.append(open(self.ENCODER_NAME[i], "r+b",buffering=0))
                    fcntl.ioctl(self.fd_channel[i], self.LOAD_CMD_REG, self.X4) 
                    fcntl.ioctl(self.fd_channel[i], self.LOAD_CMD_REG, self.IOR_DISABLE_INDEX) 
                    self.fd_channel[i].write(b'\x00\x00\x00') # Write zeros to 24 bit PR register
                    fcntl.ioctl(self.fd_channel[i], self.LOAD_CMD_REG, self.TRAN_PR_CNTR) # Transfers the PR register to the counter
                return True
            except Exception as e:
                print("Failed attempt number "+str(NumTries)+" to initialize optical encoders. Exception of type %s and args = \n"%type(e).__name__, e.args) 
                time.sleep(0.1)
                continue
        print("Failed to initialize Encoders\n")
        return False

    def close_encoders(self):
        """Closes the optical encoders
        
        returns: True if closed successfully, False if not."""
        try:
            for i in range(3):
                self.fd_channel[i].close()
            return True
        except Exception as e:
            print("Failure to close optical encoders. Exception of type %s and args = \n"%type(e).__name__, e.args )   
            return False

    def check_communications(self):
        """Checks whether communication with the motors (USB) and encoders (PCI) are working
        
        returns: True if both commincations are working, False if not."""
        serial_status = False
        try:
            serial_status = self.ser.isOpen()
        except Exception as e:
            print("No communication to stage serial bus. Exception of type %s and args = \n"%type(e).__name__, e.args)    
            serial_status = False
        encoder_status = False
        try:
            encoder_status = True
            for i in range(3):
                value = self.fd_channel[i].read(3)+b'\x00' # read the 24 bit register (3 bytes) and add a fourth byte to make it an integer.
                signed_value = struct.unpack("=I", value)[0] 
                if signed_value < 0 or signed_value > 2**24:
                    encoder_status = False
                    break
        except Exception as e:
            print("No communication to optical encoders. Exception of type %s and args = \n"%type(e).__name__, e.args)    
            encoder_status = False
        self.comm_status = serial_status and encoder_status
        return self.comm_status

    def zero_encoders(self):
        """ Reset the encoder values to zero.
        
        returns: The new encoder position readout."""
        for i in range(3):
            self.fd_channel[i].write(b'\x00\x00\x00') # Write zeros to 24 bit PR register
            fcntl.ioctl(self.fd_channel[i], self.LOAD_CMD_REG, self.TRAN_PR_CNTR) # Transfers the PR register to the counter
        read_pos=self.read_encoders()
        return read_pos

    def read_encoders(self):
        """ Reads the encoder values. Loops until the encoders have settled down to a static position.
        
        returns: The x,y, and z position of the stage relative to the last zeroed position."""
        max_diff = 100
        read_pos=[-9999999,-9999999,-9999999]
        while max_diff > 1:
            time.sleep(0.2)
            for i in range(3):
                last_read_pos = read_pos[i]
                value = self.fd_channel[i].read(3)+b'\x00' # read the 24 bit register (3 bytes) and add a fourth byte to make it an integer.
                signed_value = struct.unpack("=I", value)[0] # Convert byte string to int
                if signed_value > 2**23:
                    signed_value = signed_value - 2**24
                read_pos[i] = signed_value
                max_diff = abs(last_read_pos - read_pos[i])
            return read_pos

    def move_stage(self,x=0,y=0,z=0):
        """Moves the stage a number of stepper pulses given by the value [x, y, z].
        
        input: [x,y,z] - a list of three integer values that tell the stage how far to move in x, y, and z relative to the initial position.
        
        returns: The new encoder position readout."""
        set_pos=[x,y,z]
        for i in range(3):
            if set_pos[i] == 0:
                continue
            #print("Moving stage %s by %s steps\n"%(self.POS_NAME[i], set_pos[i]))
            self.ser.write(('F,C'+self.STEPPER_NAME[i]+str(set_pos[i])+',R').encode())
            time.sleep(0.5)
        time.sleep(0.5)
        new_pos=self.read_encoders()
        return new_pos

