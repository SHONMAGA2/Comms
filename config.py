import socket
import platform

system_info = {
    "hostname":socket.gethostname(),
    "platform":platform.system(),
    "release":platform.release()
}

HOST = '127.0.0.1'
PORT = 6500
MAX_PACKET_LENGTH = 1024 * 1024
PROTOCOL_VERSION = 1
HEADER_SIZE = 4
DEFAULT_MODULE = "TEXT"
current_modules = ["TEXT","SYSTEM"]
SOCKET_TIMEOUT = 15
