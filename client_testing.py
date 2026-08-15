from protocol import send_packet
from config import HOST,PORT
import socket

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))

    invalid_packet = {
    "module": "INVALID",
    "type": "NOTHING",
    "payload": "test"
    }

    send_packet(s,invalid_packet)