#!/usr/bin/python3
import os
import selectors
import socket
import subprocess
import sys
import traceback
import types
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
CONTENT_ENCODING = "UTF-8"

EVENT_QUIT = 0
EVENT_WRITEDATA_TO_LOCAL = (1 << 0)
EVENT_GET_RUNNING_PROCESS = (1 << 1)
EVENT_GET_INSTALLED_PROGRAM = (1 << 2)

sel = selectors.DefaultSelector()


def get_service_information_header() -> List[str]:
    """
    get remote service information : include hostname, remote timestamp, host ip
    """

    # get remote service hostname
    hostname_cp = subprocess.Popen(
        "hostname", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hostname_cp.wait()
    hostname_cp_str = hostname_cp.stdout.readlines(
    )[0].decode('ascii').strip('\r\n')

    # get remote service time
    currentTime_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # get remote service mode ip address
    host_ip_address_str = socket.gethostbyname(socket.gethostname())

    return [hostname_cp_str, currentTime_str, host_ip_address_str]


def get_service_installed_program() -> str:
    """
    return remote service all installed program
    """

    install_software_cp = subprocess.Popen(
        ["powershell", "Get-CimInstance win32_product | Select-Object Name, PackageName, InstallDate"],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = install_software_cp.communicate()
    return stdout.decode('ANSI').replace("\r\n", "\n")


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


def writeAllDataToLocal():
    """
    write data to remote service desktop
    """
    # write data to InstalledProgram.txt
    with open(os.path.join(DIRPATH, "InstalledProgram.txt"), 'w', encoding=CONTENT_ENCODING) as f:
        get_service_information_header_list = get_service_information_header()
        for content in get_service_information_header_list:
            f.write(content + '\n')
        else:
            f.write("\n")
        installed_program_str = get_service_installed_program()
        f.write(installed_program_str)

    # write data to RunningProcess.txt
    with open(os.path.join(DIRPATH, "RunningProcess.txt"), 'w', encoding=CONTENT_ENCODING) as f:
        get_service_information_header_list = get_service_information_header()
        for content in get_service_information_header_list:
            f.write(content + '\n')
        else:
            f.write("\n")
        get_service_running_process_str = get_service_running_process()
        f.write(get_service_running_process_str)


def accept_socket_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready Read Data
    print(f"Connect from {addr}")
    # conn.setblocking(False)

    # creat a variable name data pass to Selectors.data,
    # and create it's Namespace addr, inb:bytes, outb:bytes
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def socket_service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            events_mask = int(
                chr(int.from_bytes(recv_data, byteorder="little")))
            get_service_information_header_list = get_service_information_header()

            if events_mask & EVENT_WRITEDATA_TO_LOCAL:
                writeAllDataToLocal()
                data.outb += "writeDataToLocal Done!".encode(CONTENT_ENCODING)

            if events_mask & EVENT_GET_RUNNING_PROCESS:
                get_service_running_process_str = get_service_running_process()
                data.outb += get_service_running_process_str.encode(
                    CONTENT_ENCODING)

            if events_mask & EVENT_GET_INSTALLED_PROGRAM:
                installed_program_str = get_service_installed_program()
                data.outb += installed_program_str.encode(CONTENT_ENCODING)

            if not (events_mask ^ EVENT_QUIT):
                text = f"""
                Receive Bytes:q Message
                Closing Connection To {data.addr}
                Shutting Down This Service !
                """
                print(text)
                sel.unregister(sock)
                sock.close()
                sys.exit(1)
        else:
            print(f"Closing Connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            print(f"Echo {repr(data.outb)} To {data.addr}")
            # remove buffer via str slice
            data.outb = data.outb[sent:]
            try:
                # send bytes message "q" to disconnect by peer
                sock.send(b"q")
            except ConnectionError as err:
                print(
                    f"ConnectionError by peer Shutdown,Error Code:\n{err}")


def main():
    Socket = libsocketserver.Socket(HOST, DEFAULT_SOCKET_PORT)  # init Socket
    Socket.checkAndBindSocket()
    sel.register(Socket.sock, selectors.EVENT_READ,
                 data=None)  # multiplexing I/O
    try:
        while True:
            try:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_socket_wrapper(key.fileobj)
                    else:
                        socket_service_connection(key, mask)
            except Exception:
                print(f"Main error, exception for:\n{traceback.format_exc()}")
    except KeyboardInterrupt:
        print("Caught Keyboard Interrupt, Exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    main()
