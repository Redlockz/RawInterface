"""
Connection Class Module
Author: Jordi van Deerse
"""
import socket
import json
import subprocess
import time

print("Starting program")

class Connection:
    """Connection Class"""

    def __init__(self):
        """Initialize vars and prompt open function"""
        self.host = ''
        self.port = 8888
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.open()

    def welcome(self):
        """Welcome Function"""
        # De server meldt zich aan de client
        self.conn.sendall(b'Welkom Op Mijn Server, de volgende opties zijn beschikbaar:\r\n')
        self.conn.sendall(b'\t <login>: Login als een gebruiker middels Username/Password\r\n')
        self.conn.sendall(b'\t <close>: Sluit de connectie met de server\r\n')
        self.conn.sendall(b'\t <dir>: Voert het commando dir uit op de server\r\n')

    def open(self):
        """Open socket and listen to incoming connections"""
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid TIME_WAIT error
        self.s.bind((self.host, self.port))
        self.s.listen(10)
        print('> Socket luistert op poort:',self.port)
        # Wacht op self.connecties (blocking)
        self.conn, addr = self.s.accept()
        # Er is een client verbonden met de server
        print('> Verbonden met ' + addr[0] + ':' + str(addr[1]))
        self.login()

    def send(self, data):
        "Send data back to receiver"
        unicodeData = data.encode()
        self.conn.sendall(b'\r\n')
        self.conn.sendall(b''+data.encode())
        self.conn.sendall(b'\r\n')
        self.receive()

    def proces(self, data):
        "Process commands on stdin"
        print('> Client data ontvangen: '+data+' <eindeData>')
        output = subprocess.run(f"{data}", shell=True, capture_output=True, check=True)
        stdout = output
        text = f"Executed command: {data} on remote system. Got {stdout}"

        self.send(text)

    def receive(self):
        "Receive data from client after listening for connection"
        # Wacht op input van de client en geef deze ook weer terug (echo service)
        self.conn.sendall(b'Waiting for input...\r\n')
        data = False
        while not data:
            data = self.conn.recv(1024)
            data=str(data.decode('ascii')).rstrip() # # Remove \r | \n | \r\n
        self.action(data)

    def action(self, data):
        """Preform action with input"""

        match data:
            case "close":
                return self.close()
            case "dir":
                return self.proces(data)
            case "login":
                return self.login()
            case _:
                return self.receive()

    def login(self):
        """Determines if access is granted, otherwise close socket"""
        username = False
        self.conn.sendall(b'Please enter your username: \r\n')

        while not username:
            usernamebytes = self.conn.recv(1024)
            username = str(usernamebytes.decode('ascii')).rstrip()

        password = False
        self.conn.sendall(b'Please enter your password: \r\n')

        while not password:
            passwordbytes = self.conn.recv(1024)
            password = str(passwordbytes.decode('ascii')).rstrip()

        with open("config/sec.conf", "r") as f:
            print(f"> Received { username }, { password }")
            lines = f.readlines()
            user_list = []
            passwd_list = []
            for line in lines:
                jsonobject = json.loads(line)
                user_list.append([jsonobject["Username"]])
                passwd_list.append([jsonobject["Password"]])
                users = sum(user_list, [])
                passwords = sum(passwd_list, [])
            if username in users:
                print("found user")
            if password in passwords:
                print("found password")
            if username in users and password in passwords:
                self.conn.sendall(b'Login success\r\n')
                self.welcome()
                time.sleep(1)
                self.receive()
            else:
                self.conn.sendall(b'Login failed, closing connection\r\n')
                time.sleep(10) # Punish user for incorrect login by keeping connection open for longer time
                self.close()



    def close(self):
        """Close connection"""
        # Verbreek de verbinding en sluit de socket

        self.conn.close()
        self.s.close()

C = Connection()
