"""
Client Module
Author: Jordi van Deerse
"""
import socket

HOST = '127.0.0.1'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((HOST, PORT))

s.sendall(b'hee \r\n')

# time.sleep(5)
DATA = str(s.recv(1024), 'ascii')
# data=str(data.decode('ascii')).rstrip() # # Remove \r | \n | \r\n
print(DATA)
