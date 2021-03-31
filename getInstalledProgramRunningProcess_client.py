#!/usr/bin/python3
import argparse
import selectors
import socket
import types

"""
EVENT_QUIT = 0
EVENT_WRITEDATA_TO_LOCAL = (1 << 0)
EVENT_GET_RUNNING_PROCESS = (1 << 1)
EVENT_GET_INSTALLED_PROGRAM = (1 << 2)
send flag 0 will close all remote service.
send flag 1 will write all data to remote service.
send flag 2 will get running process.
send flag 4 will get installed program.
send flag 7 (1+2+4) will write all data to remote service, and get running process, installed program.
and so on flag 3, 5, 6
"""
formatter_class = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(
    description="Get windows data from remote services via socket.",
    epilog="See the document from : https://github.com/laudai/getInstalledProgramRunningProcess",
    formatter_class=formatter_class,
)
parser.add_argument(
    "-f",
    "--flag",
    help="chose the mode you want from integer 0 ~ 7 0 : Shutdown all the remote service. 1 : write choose data to remote service(can't use flag 1 only). 2 : get remote running process. 4 : get remote installed program.",
    default=6,
    type=int,
    required=True,
    choices=[0, *range(2, 8)],
)
args = parser.parse_args()
# parser.print_help()


HOST = "127.0.0.1"  # The server HOST
PORT = 17377  # The Server Port
CONTENT_ENCODING = "UTF-8"


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex((HOST, PORT))
events = selectors.EVENT_READ | selectors.EVENT_WRITE
data = types.SimpleNamespace(recv_total=0, totalmessage=b"", outb=str(args.flag).encode(CONTENT_ENCODING))

sel = selectors.DefaultSelector()
sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        """
        It will error when recv data more then recv buffer, because bytes q might mixed in message.
        """
        recv_data = sock.recv(8192)  # Should be ready to read
        if recv_data:
            if recv_data != b"q":
                # receive data to data.totalmessage
                data.totalmessage += recv_data

                # data.recv_total += len(recv_data)
                # print("\n\nreceived", repr(recv_data))
                # print(f"received {data.recv_total} characters\n")
            else:
                # print(f"total received message is :\n{data.totalmessage}\n")
                # print(f"total received {data.recv_total}\n")
                print("Closing Connection Cause Received Binary Message q")
                print(f"totalmessage length is :\n{len(data.totalmessage)}")
                sel.unregister(sock)
                sock.close()

        if not recv_data:
            print("No Receive Data ! Closing Connection !")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("sending", repr(data.outb))
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()


spreatlines = "=" * 80 + "\n"
print(spreatlines)
