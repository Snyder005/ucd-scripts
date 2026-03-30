#!/usr/bin/env ccs-script
from com.fazecast.jSerialComm import SerialPort
from com.fazecast.jSerialComm import SerialPortInvalidPortException
from ccs.data import DeviceError
import jarray

# Add support for two character read_terminator.
#   * Currently only supports single character read terminator
# (Optional) Change error handling behavior to base-hook method
#   * Add error_type, raise_error, and fmt_error to SerialDevice class
#   * Write overrides for the above to reformat as PowerError 

class SerialDevice(object):
    """Interface to a serial device.

    Parameters
    ----------
    devc_name : `str`
        Device name.
    devc_id : `str`
        Device serial port name.
    baud_rate : `int`, optional
        Serial baud rate.
    write_terminator : `str`, optional
        Write command terminator.
    read_terminator : `str`, optional
        Read operation terminator.
    """

    def __init__(self, devc_name, devc_id, baud_rate=9600, write_terminator=None, read_terminator='\n'):
        self._devc_name = devc_name
        self._devc_id = devc_id
        self._baud_rate = baud_rate
        self._write_terminator = write_terminator
        self._read_terminator = '\n' # For now ignore the entered read_terminator and use default
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
        """Initialize connection to the device.

        Raises
        ------
        DeviceError
            Raised if failed to open port.
        """
        try:
            self._port = SerialPort.getCommPort(self.devc_id)
        except SerialPortInvalidPortException as e:
            self._raise_error("invalid serial port name: {0}".format(self.devc_id), cause=e)

        self.port.setBaudRate(self.baud_rate)
        self.port.setComPortTimeouts(SerialPort.TIMEOUT_READ_BLOCKING, 1000, 0)

        self.port.openPort()
        if not self.is_connected():
            self.close()
            self._raise_error("failed to initialize device".format(self.__class__.__name__))

    def close(self):
        """Close serial port connection to the device.
        """
        self.port.closePort()

    def is_connected(self):
        """Check that status of the device connection.

        Returns
        -------
        connected : `bool`
            `True` if the device is connected. `False` if not.
        """
        return self.port.isOpen()

    def write(self, cmd):
        """Write command to the device.

        Parameters
        ----------
        cmd : `str`
            The command to write to the device, excluding write terminator.

        Raises
        ------
        DeviceError
            Raised if write operation failed.
        """
        if self.write_terminator is not None:
            cmd += self.write_terminator
        num_written = self.port.writeBytes(cmd, len(cmd))

        if num_written < 0:
            self._raise_error("error writing to serial port")

    def read(self, num_bytes=1024):
        """Read response from the device.

        Bytes are read one-by-one to a buffer until either the read terminator
        is returned, no bytes are returned, or the maximum number of bytes is 
        read.

        If no bytes are returned by the device, the read operation will
        timeout after 1000 ms. 

        Parameters
        ----------
        num_bytes : `int`, optional
            Maximum number of bytes to read (1024, by default).

        Returns
        -------
        response : `str`
            Response from the device, excluding read terminator.
        
        Raises
        ------
        DeviceError
            Raised if read operation failed.
        """
        buf = jarray.zeros(num_bytes, 'b')
        n = 0
        while n < num_bytes:
            num_read = self.port.readBytes(buf, 1, n) 
            if num_read == -1:
                self._raise_error("error reading from serial port")

            if num_read == 0:
                break

            if buf[n] == ord(self.read_terminator[0]):
                break
            n += 1
     
        return str(bytearray(buf[:n])).rstrip()

    def query(self, cmd, num_bytes=1024):
        """Query a response from the device.

        Parameters
        ----------
        cmd : `str`
            The command to write to the device, excluding write terminator.
        num_bytes : `int`, optional
            Maximum number of bytes to read (1024, by default).
        use_read_terminator : `bool`, optional
            Use the read terminator if `True`.

        Returns
        -------
        response : `str`
            Response from the device, excluding read terminator.

        Raises
        ------
        DeviceError
            Raised if read or write operation failed during query.
        """
        self.write(cmd)
        res = self.read(num_bytes)

        return res

    def _raise_error(self, message, cause=None):
        raise DeviceError(message, cause=cause)
