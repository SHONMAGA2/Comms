from config import system_info, PROTOCOL_VERSION
from protocol import send_packet

clients = {}

# ==========================
# Packet Handlers
# ==========================

def text_handler(packet):

    payload = packet.get("payload")
    print(f"Response: {payload}")


def system_handler(packet):

    payload = packet.get("payload")

    hostname = payload["hostname"]
    platform = payload["platform"]
    release = payload["release"]

    print(f"Hostname: {hostname}","Platform: {platform}","Release: {release}")

def auth_handler(conn,packet):
    client = packet.get("username")
    clients[client] = conn
    return clients
    
def routing(clients,packet):
    recipient_name = packet.get("recipient")
    recipient_conn = clients[recipient_name]
    send_packet(recipient_conn,packet)

# ==========================
# Packet Builders
# ==========================

def build_text_packet(message,username,recipient):

    return {

        "version":PROTOCOL_VERSION,"module":"TEXT","type":"MESSAGE","sender":username,"recipient":recipient,"payload":message

        }


def build_system_packet():

    return {

        "version":PROTOCOL_VERSION,"module":"SYSTEM","type":"INFO","payload":system_info

    }

def build_auth_packet(username):

    return {
        "version":PROTOCOL_VERSION,"module":"AUTH","type":"AUTH","username":username
    }


receive_handlers = {
        "TEXT":text_handler,
        "SYSTEM":system_handler,
        "AUTH":auth_handler
    }

build_handlers = {
    "TEXT":build_text_packet,
    "SYSTEM":build_system_packet,
    "AUTH":build_auth_packet
    }

def dispatch_data(conn,data):

    module_name = data.get("module")
    data_type = data.get("type")
    handler = receive_handlers.get(module_name)

    if handler is None:
        print("Unknown module")
        return None

    if module_name == "TEXT" and data_type == "MESSAGE":
        routing(clients,data)

    elif module_name == "AUTH":
        handler(conn,data)

    else:
        handler(data)

