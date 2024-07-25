import time
import socket

class Sphere(object):
    """A client-side connection to a light, photodiode, and variable aperture.

    Connections to the light, photodiode, and variable aperture are made using
    the socket module, a low-level networking interface.
    """
    def __init__(self):

        socket.setdefaulttimeout(0.5)# Timeout if no connection after 0.5 seconds

        ## Light & photodiode socket settings
        self.light_ip = '192.168.1.100'
        self.light_tcp_portnum = 51344
        self.light_buffer_size = 1024

        ## Variable aperture socket settings
        self.aperture_ip = '192.168.1.200'
        self.aperture_tcp_portnum = 4000
        self.aperture_buffer_size = 1024

        ## Variable aperture settings
        self.setting_dict = {'acceleration' : ('AC', '15'),
                             'deceleration' : ('DE', '15'),
                             'velocity' : ('VE', '1.1'),
                             'current' : ('CC', '0.2'),
                             'magnification' : ('MR', '3')}

       # Sets shutter to proper settings
        self.tolerance = 0.05
        self.light_intensity = 0.0
 
        self.initialize_light_socket()
        self.initialize_aperture_socket()
        
        #load the lookup table from most recent calibration
        with open('/home/ccd/ucd-scripts/lib/SphereLookUpTable.txt') as f:
            self.intense=f.readlines()
        self.steps=[]
        for i in range(len(self.intense)):
            self.intense[i]=float(self.intense[i])
            self.steps.append(self.intense[0]*i)
        self.steps=self.steps[:-1]
        self.intense=self.intense[1:]
        imax=max(self.intense)
        self.intense=[100*i/imax for i in self.intense]
        i=0
        while self.intense[i]<100:
            i+=1
        self.intense=self.intense[i:]
        self.steps=self.steps[i:]
        self.intense_length=len(self.intense)

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
        ## Try to initialize the aperture socket over Ethernet
        for n in range(num_tries):
            try:
                self.aperture_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.aperture_socket.connect((self.aperture_ip, self.aperture_tcp_portnum))
                break
            except Exception as e:
                time.sleep(0.1)
                continue
        ## Raise exception if out of tries
        else:
            raise e

        ## Set parameters to the proper values
        for (name, value) in list(self.setting_dict.values()):
            self.aperture_socket.send(bytes("%s\r"%(name+value)))
            time.sleep(0.1)
            self.aperture_socket.send(bytes("%s\r"%(name)))
            buff=(self.aperture_socket.recv(self.aperture_buffer_size))
            buff=buff.decode()
            buff= buff.split('=')[1]
            val = float(buff)
            test_tolerance = abs((val - float(value)) / float(value))
            if test_tolerance >= self.tolerance:
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
        diode_current=float(prefloat)

        return diode_current
    
    def calibrate_aperature(self,step=30):
        """Creates the look up table for how far open the light aperature should be to get a desired intensity.
        
        Parameters
        ----------
        step : `int`
            The number of stepper motor steps to move by. By default this is 30 which gives sub percent level resolution and will take about an hour to run."""
        stime=time.time()
        self.turn_light_on()
        step=-1*step
        
        ##Make the Look Up Table File
        file = open('/home/ccd/ucd-scripts/lib/SphereLookUpTable.txt', 'w')
        out=str(step)+"\n"
        file.write(out)
        file.close()
        
        n=0
        totalsteps=int(abs(12000/step)+2)
        tenth=int(totalsteps/10)
        for i in range(totalsteps):
            self.drive_aperture(12000)
            time.sleep(0.5)
            self.drive_aperture(step*i)
            current = self.read_photodiode()
            file = open('/home/ccd/ucd-scripts/lib/SphereLookUpTable.txt', 'a')
            file.write(str(current)+'\n')
            file.close()
            if i%tenth==0:
                print(str(10*i/tenth)+" Percent done. Took "+str(time.time()-stime)+"s")
            time.sleep(0.5)
        #Turn off the Sphere at the end
	sphere.turn_light_off()
	print("Done. Took: "+str(time.time()-stime)+"s for "+str(abs(12000/step))+" steps")
        return

    def calculate_aperture_position(self, light_intensity):
        """Calculate the required aperture position (in %) for given light 
        intensity (in %.)

        Uses A look up table (SphereLookUpTable.txt) to find the number of steps the motor must move to reach a desired percentage light intensity.

        Parameters
        ----------
        light_intensity : `float`
            Light intensity in percentage.

        Returns
        -------
        position : `float`
            The motor steps to be moved after a move of 12000 steps to open the shutter completely.
        """
        i=0
        intense_value=100
        while light_intensity<intense_value and i<self.intense_length-1:
            intense_value=self.intense[i]
            i+=1     
        return self.steps[i]
