#!/usr/bin/python3

import subprocess
import socket
import os
import wmi
from datetime import datetime

# user default write file path.
# C:\Users\{UserName}\Desktop
DIRPATH: str = os.path.join(os.environ.get("USERPROFILE"), "Desktop")
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 17777  # Port to must listen avobe on 1023


def get_client_information_header(f) -> None:
    lines = ["="*80, "\n"]
    f.writelines(lines)

    # get client hostname
    hostname_cp = subprocess.Popen(
        "hostname", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hostname_cp.wait()
    hostname_cp_str = hostname_cp.stdout.readlines()[
        0].decode("ascii").strip("\r\n")
    f.write(f"{hostname_cp_str}\n")

    # get current time
    currentTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    f.write(f"{currentTime}\n")

    # get client ip address
    host_ip_address = socket.gethostbyname(socket.gethostname())
    f.write(f"{host_ip_address}\n\n")


def get_client_install_program() -> None:
    with open(os.path.join(DIRPATH, "InstallProgram.txt"), "w") as f:
        get_client_information_header(f)

        # get client all installed program
        install_software_cp = subprocess.Popen(
            ["powershell", "Get-CimInstance win32_product | Select-Object Name, PackageName, InstallDate"],
            shell=True, stdout=f, stderr=subprocess.PIPE)
    return None


def get_client_running_process() -> None:
    disable_show_process_list = ["svchost.exe", "firefox.exe", "chrome.exe"]

    with open(os.path.join(DIRPATH, "RunningProcess.txt"), "w") as f:
        get_client_information_header(f)

        c = wmi.WMI()
        # get client running process to list structure
        # running_process_list metadata type:tuple data:(RunningProcessName, RunningProcessID)
        running_process_list = [(process.Name, process.ProcessId)
                                for process in c.Win32_Process() if process.Name not in disable_show_process_list]
        # descending via process name
        running_process_list.sort()

        foo: int = len(running_process_list)
        for running_process in running_process_list:
            if foo % 2:
                f.write(f"{running_process[0]:<40}|{running_process[1]:>20}\n")
                foo -= 1
            else:
                f.write(f"{running_process[0]:<40}={running_process[1]:>20}\n")
                foo -= 1
    return None


def main():
    # get_client_install_program()
    # get_client_running_process()
    # traceback.format_exc()}
    pass


if __name__ == "__main__":
    main()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # address family socket.AF_INET instance:( domain|IPv4 Address , Interget Port )
        #  If you pass an empty string to host, the server will accept connections on all available IPv4 interfaces
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"\nconnected by: {addr}\n")
            while True:
                data = conn.recv(1024)
                conn.send(data)
                print(data)

                if not data:
                    # conn.send(b"nodata")
                    break
