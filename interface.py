import socket
import sys
import subprocess

print("Starting program")

class Connection:

    def __init__(self):
        self.HOST = ''
        self.PORT = 8888
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.open()

    def welcome(self):
        # De server meldt zich aan de client
        self.conn.sendall(b'WelkomOpMijnServer, vertel me iets, dan zeg ik hetzelfde terug:\r\n')

    def open(self):
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid TIME_WAIT error
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(10)
        print('> Socket luistert op poort:',self.PORT)
        # Wacht op self.connecties (blocking)
        self.conn, addr = self.s.accept()
        # Er is een client verbonden met de server
        print('> Verbonden met ' + addr[0] + ':' + str(addr[1]))
        self.welcome()
        self.receive()

    def send(self, data):
        unicodeData = data.encode()
        self.conn.sendall(b'\r\n')
        self.conn.sendall(b''+data.encode())
        self.conn.sendall(b'\r\n')
        self.receive()

    def proces(self, data):
        print('> Client data ontvangen: '+data+' <eindeData>')
        output = subprocess.run(f"{data}", shell=True, capture_output=True)
        stdout = output
        text = f"Executed command: {data} on remote system. Got {stdout}"

        self.send(text)

    def receive(self):
        # Wacht op input van de client en geef deze ook weer terug (echo service)
        self.conn.sendall(b'Waiting for input...\r\n')
        data = self.conn.recv(1024)
        data=str(data.decode('ascii')).rstrip() # # Remove \r | \n | \r\n
        self.action(data)

    def action(self, data):

        match data:
            case "close":
                return self.close()
            case "dir":
                return self.proces(data)
            case _:
                return self.receive()

    def close(self):
        # Verbreek de verbinding en sluit de socket

        self.conn.close()
        self.s.close()

C = Connection()
