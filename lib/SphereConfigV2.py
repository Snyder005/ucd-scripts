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

    def __init__(self, num_tries=3):

        socket.setdefaulttimeout(0.5)# Timeout if no connection after 0.5 seconds

        ## Light & photodiode socket settings
        self.light_ip = '192.168.1.100'
        self.light_tcp_portnum = 51344
        self.light_buffer_size = 1024

        ## Variable aperture socket settings
        self.va_ip = '192.168.1.200'
        self.va_tcp_portnum = 4000
        self.va_buffer_size = 1024

        ## Variable aperture settings
        self.setting_dict = {'acceleration' : ('AC', '15'),
                             'deceleration' : ('DE', '15'),
                             'velocity' : ('VE', '1.1'),
                             'current' : ('CC', '0.2'),
                             'magnification' : ('MR', '3')}

       # Sets shutter to proper settings
        self.tolerance = 0.05
        self.light_intensity = 0.0
 
        self.initialize_light_socket(num_tries)
        self.initialize_shutter_socket(num_tries)

    def close_sockets(self):
        """Close sockets on object deletion."""
        self.light_socket.close()
        self.shutter_socket.close()

    def initialize_light_socket(self, num_tries):
        """Initializes the light socket over Ethernet.

        Parameters
        ----------
        num_tries : `int`
            Number of times to try to initialize the light socket.
        """
        ## Try to initialize the light socket
        for n in range(num_tries):
            try:
                self.light_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                self.light_socket.connect((self.light_ip, self.light_tcp_portnum))
                return
            except Exception as e:
                time.sleep(0.1)
                continue
        ## Raise exception if out of tries
        else:
            raise e
   
    def initialize_shutter_socket(self, num_tries):
        """Initialize the shutter socket over Ethernet.

        Parameters
        ----------
        num_tries: `int`
            Number of times to try to initialize the shutter socket.
        """
        ## Try to initialize the shutter socket over Ethernet
        for n in range(num_tries):
            try:
                self.shutter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.shutter_socket.connect((self.va_ip, self.va_tcp_portnum))
                break
            except Exception as e:
                time.sleep(0.1)
                continue
        ## Raise exception if out of tries
        else:
            raise e

        ## Set parameters to the proper values
        for (name, value) in list(self.setting_dict.values()):
            self.shutter_socket.send(bytes("%s\r"%(name+value)))
            time.sleep(0.1)
            self.shutter_socket.send(bytes("%s\r"%(name)))
            buff=(self.shutter_socket.recv(self.va_buffer_size))
            buff=buff.decode()
            buff= buff.split('=')[1]
            val = float(buff)
            test_tolerance = abs((val - float(value)) / float(value))
            if test_tolerance >= self.tolerance:
                self.shutter_socket.close()
                raise RuntimeError("Failed to set parameter {0} to value {1}".format(name, value))

    def verify_communications(self):
        """Verify communication status."""

        light_socket_status = (self.light_socket.getpeername()[0] == self.light_ip)
        shutter_socket_status = (self.shutter_socket.getpeername()[0] == self.va_ip)
        
        return (self.light_socket_status and self.shutter_socket_status)

    def turn_light_on(self, delay_time=4.0):
        """Turn on the light.

        Parameters
        ----------
        delay_time : `float`
            Time in seconds to wait for light stabilization.
        """
        self.light_socket.send(bytes("PS2~1\r"))
        time.sleep(delay_time)

    def turn_light_off(self, delay_time=10.0):
        """Turn off the light.

        Parameters
        ----------
        delay_time : `float`
            Time in seconds to wait for light stabilization. 
        """
        self.light_socket.send(bytes("PS2~0\r"))
        time.sleep(delay_time)

    def va_drive_shutter(self, move_value, num_waits=20):
        """Moves the variable aperture to the specified value.

        Parameters
        ----------
        move_value : `int`
            Variable aperture position specified as number of stepper motor pulses.
        num_waits: `int`
            Number of timesteps (2 seconds) to wait for move
        """
        ## Check DL status
        self.shutter_socket.send(b"DL\r")
        buff = self.shutter_socket.recv(self.va_buffer_size).decode()
        dl_status = float(buff.split('=')[1])
        if dl_status != 1.0:
            raise RuntimeError("DL value not equal to 1. Failed shutter move.")

        ## Send move command
        self.shutter_socket.send(bytes("%s\r"%('DI'+str(move_value))))
        self.shutter_socket.send(b"FL\r")

        ## Wait for move completion
        for n in range(num_waits):
            time.sleep(2)
            self.shutter_socket.send(b"RS\r")
            status = self.shutter_socket.recv(self.va_buffer_size)
            if status == b'R\r':
                break
        else:
            raise RuntimeError("Move not completed after {0} timesteps.".format(num_waits))    

        ## Check RV status
        self.shutter_socket.send(b"RV\r")
        buff = self.shutter_socket.recv(self.va_buffer_size).decode()
        rev_status = int(buff.split('=')[1])
        if RV_Status != 223:
            raise RuntimeError("RV value not equal to 223. Failed shutter move.")

    def va_set_light_intensity(self, light_intensity):
        """ Opens the shutter a specified amount given the input light intensity value.

        Parameters
        ----------
        light_intensity : `float`
            Light intensity in percentage (between 0 and 100.)
        """
        sp = self.va_calculate_shutter_position(light_intensity)
        shutter_position = int(12000 * sp / 100) - 12000

        ## Open shutter all the way
        self.va_drive_shutter(12000)
        time.sleep(0.5)

        ## Open shutter to desired amount
        self.va_drive_shutter(shutter_position)
        time.sleep(0.5)
        self.light_intensity = light_intensity

    def read_photodiode(self):
        """ Read the photodiode current.

        Returns
        -------
        diode_current : `float`
            Photodiode current in amps.
        """
        self.light_socket.send(b"D\r")
        dummy_val = self.light_socket.recv(100)
        time.sleep(0.2)
        self.light_socket.send(b"D\r")
        diode_current = float(self.light_socket.recv(100).rstrip('\r'))
        time.sleep(0.1)
        
        return diode_current

    @staticmethod
    def va_calculate_shutter_position(light_intensity):
        """Calculate the required shutter position (in %) for given light intensity (in %)

        Uses I = A + B tanh(C s + D), where s is the shutter position. Constants come from fit to photometer data

        Parameters
        ----------
        light_intensity : `float`
            Light intensity in percentage.
        """
        if light_intensity < 0.0 or light_intensity > 100.0:
            raise ValueError("Light Intensity value {0} not between 0 and 100.")

        A = 4.58586028
        B = 4.56817782
        C = 0.06850201
        D = -3.25073115
        Ap = A / (A + B)
        Bp = B / (A + B)

        if light_intensity > 99:
            return 100.0
        else:
            s = (math.atanh((light_intensity / 100.0 - Ap) / Bp) - D) / C
            return s
