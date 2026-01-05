#!/usr/bin/env ccs-script
#
#LABSPHERE LIGHT CONFIG AND FUNCTION FILE
#
# This is the configuration and function definition file for Labsphere light source in the UC Davis Viscacha, Rubin Observatory Optical beam simulator test stand.
#
#This code was largely written by Craig Lage for the Storm data aquisition system. It was edited and repurposed for the Viscacha REB5 system
# 2023 Daniel Polin
#
#Additional edits made by Adam Snyder to adapt for usage outside of a GUI environment.
#
#To Do:
# * clean up code related to look-up table
import time
import sys
import socket

socket.setdefaulttimeout(0.5)

class Sphere(object):
    """A client-side connection to a light, photodiode, and variable aperture.

    Connections to the light, photodiode, and variable aperture are made using
    the socket module, a low-level networking interface.
    """
    def __init__(self):

        self.light_ip = '192.168.1.100'
        self.light_tcp_portnum = 51344
        self.light_buffer_size = 1024
        self.initialize_light_socket()
        self.light_intensity = 0.0

        self.aperture_ip = '192.168.1.200'
        self.aperture_tcp_portnum = 4000
        self.aperture_buffer_size = 1024
        self.aperture_settings = {'AC' : '15',
                                  'DE' : '15',
                                  'VE' : '1.1',
                                  'CC' : '0.2',
                                  'MR' : '3'}
        self.initialize_aperture_socket()

        steps = []
        intensities = []
        with open('SphereLookUpTable.csv', 'r') as csvfile:

            reader = csv.DictReader(csvfile)

            for row in enumerate(reader):
                steps.append(reader['Steps'])
                intensities.append(reader['Intensity'])

            self.intensity_length = len(self.intensities)

    def close_sockets(self):
        """Close the light and aperture socket."""
        self.light_socket.close()
        self.aperture_socket.close()

    def initialize_light_socket(self, num_tries=3):
        """Initializes the light socket over Ethernet.

        Parameters
        ----------
        num_tries : `int`, (optional)
            Number of times to try to initialize the light socket.
        """
        for n in range(num_tries):
            try:
                self.light_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                self.light_socket.connect((self.light_ip, self.light_tcp_portnum))
                return
            except Exception as e:
                time.sleep(0.1)
                continue
        else:
            raise e
   
    def initialize_aperture_socket(self, num_tries=3):
        """Initialize the aperture socket over Ethernet.

        Parameters
        ----------
        num_tries: `int`, (optional)
            Number of times to try to initialize the aperture socket.

        Raises
        ------
        RuntimeError
            Raised if variable aperture parameter values cannot be set.
        """
        for n in range(num_tries):
            try:
                self.aperture_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.aperture_socket.connect((self.aperture_ip, self.aperture_tcp_portnum))
                break
            except Exception as e:
                time.sleep(0.1)
                continue
        else:
            raise e

        for (key, value) in self.aperture_settings:
            self.aperture_socket.send(bytes("{0}{1}\r".format(key, value)))
            time.sleep(0.1)
            self.aperture_socket.send(bytes("{0}\r".format(key)))
            buff = (self.aperture_socket.recv(self.aperture_buffer_size))
            buff = buff.decode()
            buff = buff.split('=')[1]
            val = float(buff)
            tolerance = abs((val - float(value)) / float(value))
            if tolerance >= 0.05:
                self.aperture_socket.close()
                raise RuntimeError("Failed to set parameter {0} to value {1}".format(name, value))

    def verify_communications(self):
        """Verify communication status.

        Returns
        -------
        status : `bool`
            `True` if socket communication is connected. `False` if not.
        """
        light_socket_status = (self.light_socket.getpeername()[0] == self.light_ip)
        aperture_socket_status = (self.aperture_socket.getpeername()[0] == self.aperture_ip)
        status = (light_socket_status and aperture_socket_status)

        return status

    def turn_light_on(self, delay_time=4.0):
        """Turn on the light.

        Parameters
        ----------
        delay_time : `float`
            Time in seconds to wait for light stabilization.
        """
        self.light_socket.send(bytes("PS2~1\r"))
        dummy_val = self.light_socket.recv(100)
        time.sleep(delay_time)

    def turn_light_off(self, delay_time=10.0):
        """Turn off the light.

        Parameters
        ----------
        delay_time : `float` (optional)
            Time in seconds to wait for light stabilization.
        """
        self.light_socket.send(bytes("PS2~0\r"))
        dummy_val = self.light_socket.recv(100)
        time.sleep(delay_time)

    def drive_aperture(self, move_value, num_waits=20):
        """Moves the variable aperture by the specified value.

        Parameters
        ----------
        move_value : `int`
            Variable aperture position specified as number of stepper motor 
            pulses.
        num_waits: `int` (optional)
            Number of timesteps (2 seconds) to wait for move.

        Raises
        ------
        RuntimeError
            Raised if the variable aperture failed to move.
        """
        ## Check DL status
        self.aperture_socket.send(b"DL\r")
        buff = self.aperture_socket.recv(self.aperture_buffer_size).decode()
        dl_status = float(buff.split('=')[1])
        if dl_status != 1.0:
            raise RuntimeError("DL value not equal to 1. Failed aperture move.")

        ## Send move command
        self.aperture_socket.send(bytes("%s\r"%('DI'+str(move_value))))
        self.aperture_socket.send(b"FL\r")

        ## Wait for move completion
        for n in range(num_waits):
            time.sleep(2)
            self.aperture_socket.send(b"RS\r")
            status = self.aperture_socket.recv(self.aperture_buffer_size)
            if status == b'R\r':
                break
        else:
            raise RuntimeError("Move not completed after {0} timesteps.".format(num_waits))    

        ## Check RV status
        self.aperture_socket.send(b"RV\r")
        buff = self.aperture_socket.recv(self.aperture_buffer_size).decode()
        rv_status = int(buff.split('=')[1])
        if rv_status != 223:
            raise RuntimeError("RV value not equal to 223. Failed aperture move.")

    def set_light_intensity(self, light_intensity):
        """ Opens the variable aperture a specified amount calculated from the
        given light intensty value.

        Parameters
        ----------
        light_intensity : `float`
            Light intensity in percentage (between 0 and 100.)
        """
        sp = self.calculate_aperture_position(light_intensity)
        aperture_position = int(sp)

        ## Open aperture all the way
        self.drive_aperture(12000)
        time.sleep(0.5)

        ## Open aperture to desired amount
        self.drive_aperture(aperture_position)
        time.sleep(0.5)
        self.light_intensity = light_intensity
        
    def read_photodiode(self):
        """ Read the photodiode current.

        Returns
        -------
        diode_current : `float`
            Photodiode current in amps.
        """

        ## Get photodiode current
        self.light_socket.send(b"D\r")
        prefloat = (self.light_socket.recv(100).rstrip('\r'))
        time.sleep(0.2)
        diode_current = float(prefloat)

        return diode_current
    
    # Clean up code
    def calculate_aperture_position(self, light_intensity):
        """Calculate the aperture position for a given light intensity.

        Uses a look up table (SphereLookUpTable.txt) to find the number of 
        steps the motor must move to reach a desired light intensity.

        Parameters
        ----------
        light_intensity : `float`
            Light intensity in percentage.

        Returns
        -------
        position : `float`
            The motor steps to be moved after a move of 12000 steps to open 
            the shutter completely.
        """
        i = 0
        intense_value = 100
        while (light_intensity < intense_value) and (i < len(self.intensities) - 1):
            intense_value = self.intensities[i]
            i += 1
        return self.steps[i]
