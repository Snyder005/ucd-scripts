#!/usr/bin/env python

#LABSPHERE LIGHT CONFIG AND FUNCTION FILE

# This is the configuration and function definition file for Labsphere light source in the UC Davis Viscacha, Rubin Observatory Optical beam simulator test stand.

#This code was largely written by Craig Lage for the Storm data aquisition system. It was edited and repurposed for the Viscacha REB5 system
# 2023 Daniel Polin

import math
import time
import sys
import socket
import logging

class Sphere(object):

    def __init__(self):

        socket.setdefaulttimeout(0.5)# Timeout if no connection after 0.5 seconds
        #*** Light & photodiode settings ***
        self.light_IP = '192.168.1.100'
        self.light_tcp_portnum = 51344
        self.buffer_size = 1024

        #*** Variable Aperture settings ***
        self.VA_TCP_IP = '192.168.1.200'
        self.VA_TCP_PORT = 4000
        self.VA_BUFFER_SIZE = 1024
        accel_value = '15' #Standard acceleration
        decel_value = '15' #Standard deceleration
        velocity_value = '1.1' #Standard velocity
        current_value = '0.2' #Standard current
        magnification_value = '3' #Standard scale

        self.Value_list = [('AC',accel_value), ('MR',magnification_value), ('DE',decel_value), ('VE',velocity_value), ('CC', current_value)]
        # Sets shutter to proper settings
        self.Tolerance = 0.05 # Checks that settings are equal to what was requested 
                         # within this tolerance.
        self.light_intensity = 0.0

    def initialize_light_socket(self):
        """Initializes the light socket over Ethernet."""
        for numTries in range(3):
            try:
                self.light_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                self.light_socket.connect((self.light_IP, self.light_tcp_portnum))
                print("Successfully initialized Light Socket\n")
                return
            except Exception as e:
                print("Failure to initialize light socket. Exception of type %s and args = \n"%type(e).__name__, e.args  )  
                time.sleep(0.1)
                continue
        print("Failed to initialize Light Socket\n")
        return

    def close_light_socket(self):
        """ Closes the light socket over Ethernet"""
        try:
            self.light_socket.close()
            print("Successfully closed Light Socket\n")
        except Exception as e:
            print("Failure to close light socket. Exception of type %s and args = \n"%type(e).__name__, e.args)    
            return
    
    def initialize_shutter_socket(self):
        # Initializes the shutter socket over Ethernet
        # And sets the parameters (speed, acceleration, etc) to the proper values
        for NumTries in range(3):
            try:
                self.shutter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.shutter_socket.connect((self.VA_TCP_IP, self.VA_TCP_PORT))
                for (Name,Value) in self.Value_list:
                    self.shutter_socket.send(bytes("%s\r"%(Name+Value)))
                    time.sleep(0.1)
                    self.shutter_socket.send(bytes("%s\r"%(Name)))
                    buff=(self.shutter_socket.recv(self.VA_BUFFER_SIZE))
                    buff=buff.decode()
                    buff= buff.split('=')[1]
                    val = float(buff)
                    print(Name, Value, val)
                    test_tolerance = abs((val - float(Value)) / float(Value))
                    if test_tolerance < self.Tolerance:
                        print("Successfully set parameter "+Name+" to value "+Value+". Measured value = "+str(val))
                    else:
                        print("Failed to set parameter "+Name+" to value "+Value)
                        print("Set-up failed.  Exiting.")
                        self.shutter_socket.close()
                        return
                print("Successfully initialized Shutter Socket\n")
                return
            except Exception as e:
                print("Failure to initialize shutter socket. Exception of type %s and args = \n"%type(e).__name__, e.args)    
                time.sleep(0.1)
                continue

        print("Failed to initialize Shutter Socket\n")
        return

    def close_shutter_socket(self):
        """ Closes the shutter socket over Ethernet"""
        try:
            self.shutter_socket.close()
            print("Successfully closed Shutter Socket\n")
            return
        except Exception as e:
            print("Failure to close shutter socket. Exception of type %s and args = \n"%type(e).__name__, e.args)    
            return

    def check_communications(self):
        # Checks on communications staus
        self.light_socket_status = False
        try:
            test_IP = self.light_socket.getpeername()[0]
            if test_IP == self.light_IP:
                self.light_socket_status = True
        except Exception as e:
            print("Light socket not communicating. Exception of type %s and args = \n"%type(e).__name__, e.args)    
            self.light_socket_status = False

        self.shutter_socket_status = False
        try:
            test_IP = self.shutter_socket.getpeername()[0]
            if test_IP == self.VA_TCP_IP:
                self.shutter_socket_status = True
        except Exception as e:
            print("Shutter socket not communicating. Exception of type %s and args = \n"%type(e).__name__, e.args)    
        self.comm_status = self.light_socket_status and self.shutter_socket_status
        return


    def turn_light_on(self):
        # Turns the light on
        print("Turning light on - 4 second delay for stabilization.")
        self.light_socket.send(bytes("PS2~1\r"))
        time.sleep(4)
        self.read_photodiode()
        return

    def turn_light_off(self):
        # Turns the light off
        print("Turning light off - 8 second delay for stabilization.")
        self.light_socket.send(bytes("PS2~0\r"))
        time.sleep(8)
        self.read_photodiode()
        return

    def final_light_off(self):
        # Turns the light off at program exit without updating photodiode current
        print("Turning light off")
        self.light_socket.send("PS2~0\r")
        return

    def va_drive_shutter(self, Move_value):
        # Moves the shutter to a value specified by a Move_value
        # Move_value is a number of stepper motor pulses
        # 12000 = open all the way
        self.shutter_socket.send(b"DL\r")
        buff=(self.shutter_socket.recv(self.VA_BUFFER_SIZE))
        buff=buff.decode()
        buff= buff.split('=')[1]
        DL_Status = float(buff)
        if DL_Status != 1.0:
                print("DL value not equal to 1. Failed shutter move. Exiting.")
                sys.exit()
        print("DL_Status = ",DL_Status)

        self.shutter_socket.send(bytes("%s\r"%('DI'+str(Move_value))))
        self.shutter_socket.send(b"FL\r")

        Move_Success = False
        for NumTries in range(20):
                time.sleep(2)
                self.shutter_socket.send(b"RS\r")
                Status = self.shutter_socket.recv(self.VA_BUFFER_SIZE)
                print("Status = ", Status.decode())
                if Status == b'R\r':
                        Move_Success = True
                        break
        self.shutter_socket.send(b"RV\r")
        buff=(self.shutter_socket.recv(self.VA_BUFFER_SIZE))
        buff=buff.decode()
        buff= buff.split('=')[1]
        RV_Status = int(buff)
        if RV_Status != 223:
                print("RV value not equal to 223. Failed shutter move. Exiting.")
                sys.exit()
        if Move_Success:
                print("Successfully moved shutter as requested")
        else:
                print("Number of status tests exceeded.  Failed shutter move. Exiting.")
                sys.exit()
        return

    def va_calculate_shutter_position(self, light_intensity):
        """ Calculates the required shutter position (in %) to give the desired light intensity (in %).
	 Uses I = A + B tanh(C s + D), where s is the shutter position. Constants come from fit to photometer data"""
        A = 4.58586028
        B = 4.56817782
        C = 0.06850201
        D = -3.25073115
        Ap = A / (A + B)
        Bp = B / (A + B)

        if light_intensity < 1.0:
            print("Light intensity not accurate for intensities < 1%.\n")
        elif light_intensity > 99:
            print("Light intensity not accurate for intensities >99%.  Opening shutter all the way.\n")
            return 100.0
 
        s = (math.atanh((light_intensity / 100.0 - Ap) / Bp) - D) / C
        return s

    def va_set_light_intensity(self, light_intensity):
        """ Opens the shutter a specified amount given the input light intensity value.  Assumes 0.0 < Value < 100."""
        print("Set Light Intensity to %f"%light_intensity )
        if light_intensity < 0.0 or light_intensity > 100.0:
            print("Light Intensity value not between 0 and 100. Exiting")
            sys.exit()

        self.va_drive_shutter(12000)
        # This opens the shutter all the way
        print("Opening shutter completely for calibration.")
        time.sleep(0.5)

        sp = self.va_calculate_shutter_position(light_intensity)
        # This linearizes the non-linearity of the shutter
        Shutter_Position = int(12000 * sp / 100) - 12000
        self.va_drive_shutter(Shutter_Position)
        # This opens the shutter the requested amount
        time.sleep(0.5)
        self.light_intensity=light_intensity
        self.read_photodiode()
        return

    def read_photodiode(self):
        """ Reads the photodiode current and returns the value in amps"""
        self.light_socket.send(b"D\r")
        dummy_val = self.light_socket.recv(100)
        time.sleep(0.2)
        self.light_socket.send(b"D\r")
        self.diode_current = self.light_socket.recv(100)
        diode_out=(str(self.diode_current).rstrip('\r'))
        time.sleep(0.1)
        print("Light Intensity "+diode_out+"Amperes")
        return diode_out
