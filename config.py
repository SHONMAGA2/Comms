import socket
import platform

system_info = {
    "hostname":socket.gethostname(),
    "platform":platform.system(),
    "release":platform.release()
}

HOST = '192.168.0.107'
PORT = 6500
MAX_PACKET_LENGTH = 1024 * 1024
PROTOCOL_VERSION = 1
HEADER_SIZE = 4
DEFAULT_MODULE = "TEXT"
current_modules = ["TEXT","SYSTEM"]

