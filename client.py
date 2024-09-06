"""
Client Module
Author: Jordi van Deerse
"""
import socket
# import sys
import subprocess
import time

HOST = '127.0.0.1'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid TIME_WAIT error
# s.bind((HOST, PORT))
s.connect((HOST, PORT))


# conn, addr = s.accept()
message = "hello"
print(f"sending {message} to ")
s.sendall(b'hee \r\n')

# time.sleep(5)
data = str(s.recv(1024), 'ascii')
# data=str(data.decode('ascii')).rstrip() # # Remove \r | \n | \r\n
print(data)