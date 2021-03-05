import errno
import socket
from typing import Tuple, Union


class Socket:
    def __init__(self, HOST: str, DEFAULT_SOCKET_PORT: Tuple[int]):
        self.HOST = HOST
        self.DEFAULT_SOCKET_PORT = DEFAULT_SOCKET_PORT
        self.PORT: Union[int, None] = None
        # super().__init__()

    def checkAndBindSocket(self):
        """
        Check port is binding, return socket instance
        """
        for socketport in range(self.DEFAULT_SOCKET_PORT[0], self.DEFAULT_SOCKET_PORT[1] + 1):
            try:
                # Use IPv4 , TCP Protocol socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind((self.HOST, socketport))
                self.PORT = socketport
                self.sock.listen()
                print(f"Socket Server use Address:{self.HOST}\tPort:{self.PORT}")
                self.sock.setblocking(False)  # non-block socket
                break
                """
                or you can use this to avoid  port already use
                # Avoid bind() exception: OSError: [Errno 48] Address already in use
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                """
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    print(f"Port {socketport} is already in use.")
                else:
                    print(f"Other socket error exception :\n{e}")
