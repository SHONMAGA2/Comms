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

def client_list_handle(conn):
    client_usernames = list(clients.keys())
    print(f"Connected clients: {client_usernames}")
    
    send_packet(conn,client_usernames)
    
def auth_handler(conn,packet):
    client = packet.get("payload")

    if client in clients:
        print(f"Username already in use: {client}")
        return False

    clients[client] = conn

    print(f"Authenticated client: {client}")
    
def routing(conn,clients,packet):
    recipient_name = packet.get("recipient")
    recipient_conn = clients.get(recipient_name)

    if recipient_conn is None:
        error_packet = {
            "version": PROTOCOL_VERSION,
            "module": "SYSTEM",
            "type": "ERROR",
            "payload": f"{recipient_name} is offline"
        }

        send_packet(conn, error_packet)
        return

    send_packet(recipient_conn,packet)

# ==========================
# Packet Builders
# ==========================

def build_text_packet(message,username,recipient):

    return {

        "version":PROTOCOL_VERSION,"module":"TEXT","type":"MESSAGE","sender":username,"recipient":recipient,"payload":message

        }

def build_client_list_request(message):

    return {
    
            "version":PROTOCOL_VERSION,"module":"SYSTEM","type":"CLIENT_LIST","payload":message
    
            }

def build_system_packet():

    return {

        "version":PROTOCOL_VERSION,"module":"SYSTEM","type":"INFO","payload":system_info

    }

def build_auth_packet(username):

    return {
        "version":PROTOCOL_VERSION,"module":"AUTH","type":"AUTH","payload":username
    }


receive_handlers = {
        "TEXT":text_handler,
        "SYSTEM":{"type":{"INFO":system_handler,"CLIENT_LIST":client_list_handle}},
        "AUTH":auth_handler
    }

build_handlers = {
    "TEXT":build_text_packet,
    "SYSTEM":{"type":{"INFO":build_system_packet,"CLIENT_LIST":build_client_list_request}},
    "AUTH":build_auth_packet
    }

def dispatch_data(conn,data):

    module_name = data.get("module")
    data_type = data.get("type")

    if module_name == "TEXT" and data_type == "MESSAGE":
        routing(conn,clients,data)

    elif module_name == "SYSTEM" and data_type == "INFO":
        system_handle = receive_handlers["SYSTEM"]["type"]["INFO"]

        system_handle(data)

    elif module_name == "SYSTEM" and data_type == "CLIENT_LIST":
        client_list_handle(conn)

    elif module_name == "AUTH":
        auth_handle = receive_handlers["AUTH"]
        auth_handle(conn,data)

    elif module_name == "SYSTEM" and data_type == "ERROR":
        print(data.get("payload"))

    else:
        print("Unknown packet type")

