#!/usr/bin/env ccs-script
from xyz.froud.jvisa import JVisaResourceManager, JVisaException
from com.fazecast.jSerialComm import SerialPort

import jarray

# Add support for read_terminator

class SerialDevice(object):
    """Interface to a serial device.

    Parameters
    ----------
    devc_name : `str`
        Device name.
    devc_id : `str`
        Device resource name.
    baud_rate : `int`, optional
        Serial baud rate.
    write_terminator : `str`, optional
        Write command terminator.
    read_terminator : `str`, optional
        Read operation terminator.
    """

    def __init__(self, devc_name, devc_id, baud_rate=None, write_terminator=None, read_terminator=None):
        self._devc_name = devc_name
        self._devc_id = devc_id
        self._baud_rate = baud_rate
        self._write_terminator = write_terminator
        self._read_terminator = read_terminator # Not used
        self._port = None # Needed?
        self.initialize()

    @property
    def devc_name(self):
        """Device name (`str`).
        """
        return self._devc_name

    @property
    def devc_id(self):
        """Device resource name (`str`).
        """
        return self._devc_id

    @property
    def baud_rate(self):
        """Serial baud rate (`int`).
        """
        return self._baud_rate

    @property
    def write_terminator(self):
        """Write command terminator (`str`).
        """
        return self._write_terminator

    @property
    def read_terminator(self):
        """Read operation terminator (`self`).
        """
        return self._read_terminator

    @property
    def port(self):
        """A serial port (`com.fazecast.jSerialComm.SerialPort`).
        """
        return self._port

    def initialize(self):
        self._port = SerialPort.getCommPort(self._devc_id) # can throw an exception if devc_id is not identified
        if self.baud_rate is not None:
            self.port.setBaudRate(self.baud_rate)
        self.port.setComPortTimeouts(SerialPort.TIMEOUT_READ_BLOCKING, 1000, 0) # check parameters, is read timeout of 1000ms needed?
        self.port.openPort()

        if not self.is_connected(): # Throw exception if not connected
            self.close()
            raise IOError("Failed to open port {0}".format(self._devc_id))

    def close(self):
        if self.port.isOpen():
            self.port.closePort()

    def is_connected(self):
        return self.port.isOpen()

    def write(self, cmd):
        cmd = cmd + self._write_terminator
        n = self.port.writeBytes(cmd, len(cmd))

        if n < 0: # Throw exception if write failes
            raise IOError("Write failed.") # Replace with custom error

    def read(self, num_bytes=1024):

        buff = jarray.zeros(num_bytes, 'b')
        n = self.port.readBytes(buff, len(buff))

        return str(bytearray(buff[:n])).rstrip() if n > 0 else str()

    def query(self, cmd, num_bytes=1024):
        self.write(cmd)
        res = self.read(num_bytes)

        return res
