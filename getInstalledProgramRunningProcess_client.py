#!/usr/bin/python3

import selectors
import socket
import sys
import types

"""
must use argparse
import argparse
"""
"""
0
1
2
4
7
"""

sel = selectors.DefaultSelector()

HOST = "127.0.0.1"  # The server HOST
PORT = 17377  # The Server Port
CONTENT_ENCODING = "UTF-8"


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex((HOST, PORT))
events = selectors.EVENT_READ | selectors.EVENT_WRITE
data = types.SimpleNamespace(
    recv_total=0, totalmessage=b"", outb=sys.argv[1].encode(CONTENT_ENCODING))

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


spreatlines = "="*80 + "\n"
print(spreatlines)
