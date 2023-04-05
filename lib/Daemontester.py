import socket
import os
import time

# Set up the socket to send commands
s = socket.socket()
host = socket.gethostname()
port = 12346
tstart=time.time()
s.connect((host, port))

s.sendall("close_shutter".encode())

# Close the socket
s.close()
