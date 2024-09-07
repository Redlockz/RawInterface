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

        self.conn.sendall(b'Welcome to my server, the next options are available:\r\n')
        self.conn.sendall(b'\t <login>: Login as a user using Username/Password authentication\r\n')
        self.conn.sendall(b'\t <CMD>: Go to the option to execute a command and receive return value\r\n')
        self.conn.sendall(b'\t <close>: Closes the connection to the server server\r\n')

    def open(self):
        """Open socket and listen to incoming connections"""

        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid TIME_WAIT error
        self.s.bind((self.host, self.port))
        self.s.listen(10)
        print('> Socket luistert op poort:',self.port)
        # Wacht op self.connecties (blocking)
        self.conn, self.addr = self.s.accept()
        # Er is een client verbonden met de server
        print('> Verbonden met ' + self.addr[0] + ':' + str(self.addr[1]))
        self.login()

    def send(self, data):
        "Send data back to receiver"

        self.conn.sendall(b'\r\n')
        self.conn.sendall(b''+data.encode())
        self.conn.sendall(b'\r\n')
        self.receive()

    def proces(self, data):
        "Process commands on stdin"

        executionorder = False
        self.conn.sendall(b'Please enter the command you want to execute: \r\n')

        # Wait for user input
        while not executionorder:
            executionorderbytes = self.conn.recv(1024)
            executionorder = str(executionorderbytes.decode('ascii')).rstrip()
        print('> Received client data <begin>: '+executionorder+' <end>')
        output = subprocess.run(f"{executionorder}", shell=True, capture_output=True, check=True)
        stdout = output
        text = f"Executed command: {executionorder} on remote system. Got {stdout}"

        self.send(text)

    def receive(self):
        "Receive data from client"

        self.conn.sendall(b'Waiting for input...\r\n')
        data = False
        while not data:
            data = self.conn.recv(1024)
            data=str(data.decode('ascii')).rstrip()
        self.action(data)

    def action(self, data):
        """Preform action with input from receive function"""

        match data:
            case "close":
                return self.close()
            case "CMD":
                return self.proces(data)
            case "login":
                return self.login()
            case _:
                return self.receive()

    def login(self):
        """Determines if access is granted, otherwise close socket"""

        username = False
        self.conn.sendall(b'Please enter your username: \r\n')

        # Wait for user input
        while not username:
            usernamebytes = self.conn.recv(1024)
            username = str(usernamebytes.decode('ascii')).rstrip()

        password = False
        self.conn.sendall(b'Please enter your password: \r\n')

        # Wait for user input
        while not password:
            passwordbytes = self.conn.recv(1024)
            password = str(passwordbytes.decode('ascii')).rstrip()

        # Open user file
        with open("config/sec.conf", "r") as f:
            print(f"> Received { username }, { password }")
            lines = f.readlines()
            user_list = []
            passwd_list = []
            for line in lines:

                jsonobject = json.loads(line)

                # Load user dict for specific user
                if username == jsonobject["Username"]:
                    user_list.append([jsonobject["Username"]])
                    passwd_list.append([jsonobject["Password"]])
                    users = sum(user_list, [])
                    passwords = sum(passwd_list, [])

            # logging
            if username in users:
                print("found user")
            if password in passwords:
                print("found password")

            # Determine success of authentication
            if username in users and password in passwords:
                print("Login success, listening for user input...")
                self.conn.sendall(b'Login success\r\n')
                self.welcome()
                time.sleep(1)
                self.receive()
                # TODO: Return Token
                # TODO: Create decorator to validate token
            else:
                self.conn.sendall(b'Login failed, closing connection\r\n')
                time.sleep(10) # Punish user for incorrect login by keeping connection open for longer time
                self.close()

    def close(self):
        """Close connection"""

        print('> \t Closing connection with'+ self.addr[0] + ':' + str(self.addr[1]))
        self.conn.close()
        self.s.close()

C = Connection()
