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
import time
import sys
import socket

socket.setdefaulttimeout(0.5)

class Sphere(object):
    """A client-side connection to a light, photodiode, and variable aperture.

    Connections to the light, photodiode, and variable aperture are made using
    the socket module, a low-level networking interface.

    Parameters
    ----------
    light_ip : `str`
        Light IP address.
    light_tcp : `int` 
        Light TCP port number.
    aperture_ip : `str`
        Variable aperture IP address.
    aperture_tcp : `int`
        Variable aperture TCP port number.
    look_up_table : `str`
        Look up table CSV filename.
    bufsize : `int`, optional
        Maximum number of bytes to receive from connected socket (1024, by default).
    """

    def __init__(self, light_ip, light_tcp, aperture_ip, aperture_tcp, look_up_table):

        self.light_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        self.light_socket.connect((light_ip, light_tcp_portnum))
        self.light_intensity = 0.0

        self.aperture_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.aperture_socket.connect((aperture_ip, aperture_tcp_portnum))

        settings = {'AC' : '15',
                    'DE' : '15',
                    'VE' : '1.1',
                    'CC' : '0.2',
                    'MR' : '3'}
        for (key, value) in settings:
            self.aperture_socket.send(bytes("{0}{1}\r".format(key, value)))
            time.sleep(0.1)
            self.aperture_socket.send(bytes("{0}\r".format(key)))
            msg = self.aperture_socket.recv(1024).decode()
            val = float(msg.split('=')[1])
            tolerance = abs((val - float(value)) / float(value))
            if tolerance >= 0.05:
                self.light_socket.close()
                self.aperture_socket.close()
                raise RuntimeError("Failed to set parameter {0} to value {1}".format(key, value))

        self.motor_steps = []
        self.light_intensities = []
        with open(look_up_table, 'r') as csvfile:

            reader = csv.DictReader(csvfile)

            for row in enumerate(reader):
                self.motor_steps.append(reader['Steps'])
                self.light_intensities.append(reader['Intensity'])

    def turn_light_on(self, wait=4.0):
        """Turn on the light.

        Parameters
        ----------
        wait : `float`
            Time in seconds to wait for light stabilization.
        """
        self.light_socket.send(bytes("PS2~1\r"))
        _ = self.light_socket.recv(100)
        time.sleep(wait)

    def turn_light_off(self, wait=10.0):
        """Turn off the light.

        Parameters
        ----------
        wait : `float` (optional)
            Time in seconds to wait for light stabilization.
        """
        self.light_socket.send(bytes("PS2~0\r"))
        _ = self.light_socket.recv(100)
        time.sleep(wait)

    def drive_aperture(self, motor_steps, num_waits=20):
        """Moves the variable aperture by the specified value.

        Parameters
        ----------
        motor_steps : `int`
            Number of steps for the motor to move.
        num_waits: `int` (optional)
            Number of timesteps (2 seconds) to wait for move.

        Raises
        ------
        RuntimeError
            Raised if the variable aperture failed to move.
        """
        self.aperture_socket.send(b"DL\r")
        msg = self.aperture_socket.recv(1024).decode()
        dl_status = float(msg.split('=')[1])
        if dl_status != 1.0:
            raise RuntimeError("DL value not equal to 1. Failed aperture move.")

        self.aperture_socket.send(b"{0}\r".format('DI'+str(motor_steps)))
        self.aperture_socket.send(b"FL\r")

        for n in range(num_waits):
            time.sleep(2)
            self.aperture_socket.send(b"RS\r")
            msg = self.aperture_socket.recv(1024)
            if msg == b'R\r':
                break
        else:
            raise RuntimeError("Move not completed after {0} timesteps.".format(num_waits))    

        self.aperture_socket.send(b"RV\r")
        msg = self.aperture_socket.recv(1024).decode()
        rv_status = int(msg.split('=')[1])
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
        self.drive_aperture(12000)
        time.sleep(0.5)

        motor_steps = self.get_motor_steps(light_intensity)
        self.drive_aperture(motor_steps)
        time.sleep(0.5)
        self.light_intensity = light_intensity
        
    def read_photodiode(self):
        """ Read the photodiode current.

        Returns
        -------
        current : `float`
            Photodiode current in amps.
        """
        self.light_socket.send(b"D\r")
        msg = (self.light_socket.recv(100).rstrip('\r'))
        time.sleep(0.2)
        current = float(msg)

        return current
    
    def get_motor_steps(self, light_intensity):
        """Get the motor steps to move to achieve a given light intensity.

        Parameters
        ----------
        light_intensity : `float`
            Light intensity in percentage.

        Returns
        -------
        motor_steps : `float`
            Number of steps for the motor to move.
        """
        closest = min(self.light_intensities, key=lambda x: abs(x-light_intensity))
        index = self.light_intensities.index(closest)
        motor_steps = self.motor_steps[index]

        return motor_steps
