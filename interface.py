"""
Connection Class Module
Author: Jordi van Deerse
"""
import socket
import json
import subprocess
import time
import logging
import sys

print("Starting program")

class Connection:
    """Connection Class"""

    def __init__(self):
        """Initialize vars and prompt open function"""

        self.host = ''
        self.port = 8888

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                            handlers=[
                                logging.FileHandler('log/Socket.log'),
                                logging.StreamHandler(sys.stdout)
                            ],
                            encoding='utf-8',
                            level=logging.INFO)

        self.open()

    def welcome(self):
        """Welcome Function"""

        self.logger.info("> User has been authorized")

        self.conn.sendall(b'Welcome to my server, the next options are available:\r\n')
        self.conn.sendall(b'\t <login>: Login as a user using Username/Password authentication\r\n')
        self.conn.sendall(b'\t <CMD>: Go to the option to execute a command and receive return value\r\n')
        self.conn.sendall(b'\t <close>: Closes the connection to the server server\r\n')

    def open(self):
        """Open socket and listen to incoming connections"""

        self.logger.info(f"Trying to open port: {self.port}")

        try:
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid TIME_WAIT error
            self.s.bind((self.host, self.port))
            self.s.listen(10)
            self.logger.info(f'Socket listening on port: {self.port}')
        except exception as e:
            self.logger.debug(f"Could not open {self.host}:{self.port}.")
            self.logger.debug(f"{e}")
        # Wacht op self.connecties (blocking)
        self.conn, self.addr = self.s.accept()
        # Er is een client verbonden met de server
        self.logger.info('Connected to ' + self.addr[0] + ':' + str(self.addr[1]))
        self.login()

    def send(self, data):
        "Send data back to receiver"

        self.conn.sendall(b'\r\n')
        try:
            self.conn.sendall(b''+data.encode())
            self.logger.info(f"send {data} to {self.addr[0],self.addr[1]}")
        except exception as e:
            self.logger.debug(f"Could not parse {data}")
        self.conn.sendall(b'\r\n')
        self.receive()

    def proces(self):
        "Process commands on stdin"

        self.logger.info("Entering Command execution mode")

        executionorder = False
        self.conn.sendall(b'Please enter the command you want to execute: \r\n')

        # Wait for user input
        while not executionorder:
            executionorderbytes = self.conn.recv(1024)
            executionorder = str(executionorderbytes.decode('ascii')).rstrip()

        self.logger.info('Received client data <begin>: '+executionorder+' <end>')
        try:
            output = subprocess.run(f"{executionorder}", shell=True, capture_output=True, check=True)
            stdout = output
            text = f"Executed command: {executionorder} on remote system. Got {stdout}"
            self.logger.info(f"{text}")
        except exception as e:
            self.logger.debug(f"Could not process command {executionorder}")
            self.logger.debug(f"{e}")

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
                self.logger.info("Entering Close Function")
                return self.close()
            case "CMD":
                self.logger.info("Entering Proces Function")
                return self.proces()
            case "login":
                self.logger.info("Entering Login Function")
                return self.login()
            case _:
                self.logger.info(f"Could not parse request, got {data}")
                self.logger.info("Entering Receive Function")
                return self.receive()

    def login(self):
        """Determines if access is granted, otherwise close socket"""

        username = False
        self.conn.sendall(b'Please enter your username: \r\n')

        self.logger.info("Waiting for username")

        # Wait for user input
        while not username:
            usernamebytes = self.conn.recv(1024)
            username = str(usernamebytes.decode('ascii')).rstrip()

        password = False
        self.conn.sendall(b'Please enter your password: \r\n')

        self.logger.info("Waiting for password")

        # Wait for user input
        while not password:
            passwordbytes = self.conn.recv(1024)
            password = str(passwordbytes.decode('ascii')).rstrip()

        # Open user file
        try:
            with open("config/sec.conf", "r") as f:
                self.logger.info(f"Received { username }, { password }")
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
        except exception as e:
            self.logger.debug(f"Could not parse request for {username, password}")
            self.logger.debug(f"{e}")

        # logging
        if username in users:
            self.logger.info("found user")
        if password in passwords:
            self.logger.info("found password")

        # Determine success of authentication
        if username in users and password in passwords:
            self.logger.info("Login success, listening for user input...")
            self.conn.sendall(b'Login success\r\n')
            self.welcome()
            time.sleep(1)
            self.receive()
            # FIXME: Return Token
            # FIXME: Create decorator to validate token
        else:
            self.conn.sendall(b'Login failed, closing connection\r\n')
            # Punish user for incorrect login by keeping connection open for longer time
            time.sleep(10)
            self.close()

    def close(self):
        """Close connection"""

        self.logger.info('> Closing connection with'+ self.addr[0] + ':' + str(self.addr[1]))
        self.conn.close()
        self.s.close()

C = Connection()
