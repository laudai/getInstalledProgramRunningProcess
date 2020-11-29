#!/usr/bin/python3
import os
import selectors
import socket
import subprocess
import sys
import traceback
from datetime import datetime
from typing import List

import wmi

import libsocketserver

""""
cp means child process
"""

# user default write file path.
# C:\Users\%UserName%\Desktop
DIRPATH: str = os.path.join(os.environ.get("USERPROFILE"), "Desktop")
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
# Port must listen above on 1023
# Service Port range in 17377 ~ 17777
DEFAULT_SOCKET_PORT: tuple = (17377, 17777)

sel = selectors.DefaultSelector()


def get_service_information_header() -> List[str]:
    """
    get remote service information : include hostname, remote timestamp, host ip
    """

    lines = "="*80 + "\n"

    # get remote service hostname
    hostname_cp = subprocess.Popen(
        "hostname", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hostname_cp.wait()
    hostname_cp_str = hostname_cp.stdout.readlines(
    )[0].decode('ascii').strip('\r\n') + "\n"

    # get remote service time
    currentTime_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\n"

    # get remote service mode ip address
    host_ip_address = socket.gethostbyname(socket.gethostname())
    host_ip_address_str = host_ip_address + "\n\n"

    return [lines, hostname_cp_str, currentTime_str, host_ip_address_str]


def get_service_installed_program() -> str:
    """
    return remote service all installed program
    """

    install_software_cp = subprocess.Popen(
        ["powershell", "Get-CimInstance win32_product | Select-Object Name, PackageName, InstallDate"],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = install_software_cp.communicate()
    return stdout.decode('ANSI').strip()


def get_service_running_process() -> str:
    """
    get remote service all running process exclude the DISABLE_SHOW_PROCESS_LIST
    """
    DISABLE_SHOW_PROCESS_LIST = ["svchost.exe", "firefox.exe", "chrome.exe"]

    c = wmi.WMI()
    # get remote service running process to list structure
    # running_process_list metadata type:tuple data:(RunningProcessName, RunningProcessID)
    running_process_list = [(process.Name, process.ProcessId)
                            for process in c.Win32_Process() if process.Name not in DISABLE_SHOW_PROCESS_LIST]
    # descending via process name
    running_process_list.sort()

    foo: int = len(running_process_list)
    running_process_str: str = f"{'ProcessName':<40}={'Process ID':>20}\n" if foo % 2 else f"{'ProcessName':<40}|{'Process ID':>20}\n"
    for running_process in running_process_list:
        if foo % 2:
            running_process_str += f"{running_process[0]:<40}|{running_process[1]:>20}\n"
            foo -= 1
        else:
            running_process_str += f"{running_process[0]:<40}={running_process[1]:>20}\n"
            foo -= 1
    return running_process_str


def writeData():
    """
    write data to remote service desktop
    """
    # write data to InstalledProgram.txt
    with open(os.path.join(DIRPATH, "InstalledProgram.txt"), 'w', encoding='UTF-8') as f:
        get_service_information_header_list = get_service_information_header()
        for content in get_service_information_header_list:
            f.write(content)
        installed_program_text = get_service_installed_program()
        f.write(installed_program_text)

    # write data to RunningProcess.txt
    with open(os.path.join(DIRPATH, "RunningProcess.txt"), 'w', encoding='UTF-8') as f:
        get_service_information_header_list = get_service_information_header()
        for content in get_service_information_header_list:
            f.write(content)
        get_service_running_process_str = get_service_running_process()
        f.write(get_service_running_process_str)


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == "write":
            writeData()
    # traceback.format_exc()}


if __name__ == "__main__":
    # main()
    Socket = libsocketserver.Socket(HOST, DEFAULT_SOCKET_PORT)  # init Socket
    Socket.checkAndBindSocket()
    sel.register(Socket.sock, selectors.EVENT_READ,
                 data=None)  # multiplexing I/O

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     # address family socket.AF_INET instance:( domain|IPv4 Address , Interget Port )
    #     #  If you pass an empty string to host, the server will accept connections on all available IPv4 interfaces
    #     s.bind((HOST, PORT))
    #     s.listen()
    #     conn, addr = s.accept()
    #     with conn:
    #         print(f"\nconnected by: {addr}\n")
    #         while True:
    #             data = conn.recv(1024)
    #             conn.send(data)
    #             print(data)

    #             if not data:
    #                 # conn.send(b"nodata")
    #                 break
