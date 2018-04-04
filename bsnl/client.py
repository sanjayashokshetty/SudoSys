#!/bin/python
import socket
s=socket.socket()
host=socket.gethostname()
port=1235
s.connect((host,port))
print(s.recv(1024))
while True:
    pass
