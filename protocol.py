import json
import struct
from config import MAX_PACKET_LENGTH, HEADER_SIZE,PROTOCOL_VERSION,current_modules

def recv_exact(sock,size):
        data = b""

        while len(data) < size:
            chunk = sock.recv(size - len(data))

            if not chunk:
                return None

            data += chunk

        return data

def send_packet(sock,packet):

    payload = json.dumps(packet).encode('utf-8')

    packet_length = len(payload)
    header = struct.pack("!I",packet_length)

    sock.sendall(header + payload)

def receive_packet(sock):
    header = recv_exact(sock,HEADER_SIZE)

    if header is None:
        return None

    length = struct.unpack("!I",header)[0]


    if length >  MAX_PACKET_LENGTH:
        print("packet length too large ")
        return None

    if length == 0:
        print("Empty packet")
        return None

    payload = recv_exact(sock,length)

    if payload is None:
        return None

    try:
        data = json.loads(payload.decode('utf-8'))

    except json.JSONDecodeError as e:
        raise ValueError(f"Packet contains invalid JSON: {e}") from e

    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8: {e}") from e

    return data

# Single Packet Processing Function

def process_packet(sock):

    data = receive_packet(sock)

    if data is None:
        print("server connection closed ")
        return None

    if not isinstance(data,dict):
        raise TypeError("Packet data should be a dictionary")
        

    if "version" not in data:
        raise ValueError("Missing required field: version")
        

    packet_version = data.get("version")
    if packet_version != PROTOCOL_VERSION:
        raise ValueError("Invalid packet version")

    if "module" not in data:
        raise ValueError("Missing required field: module")


    packet_module = data.get("module")

    if not isinstance(packet_module, str):
        raise TypeError("Packet module should be a string")

    if packet_module not in current_modules:
        raise ValueError("Invalid packet module")

    if "payload" not in data:
        raise ValueError("Missing required field: payload")

    return data