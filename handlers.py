from config import system_info, PROTOCOL_VERSION

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

# ==========================
# Packet Builders
# ==========================

def build_text_packet(message):

    return {

        "version":PROTOCOL_VERSION,"module":"TEXT","type":"MESSAGE","payload":message

        }


def build_system_packet():

    return {

        "version":PROTOCOL_VERSION,"module":"SYSTEM","type":"INFO","payload":system_info

    }

receive_handlers = {
        "TEXT":text_handler,
        "SYSTEM":system_handler
    }

build_handlers = {
    "TEXT":build_text_packet,
    "SYSTEM":build_system_packet
    }

def dispatch_data(data):

    module_name = data.get("module")
    handler = receive_handlers.get(module_name)

    if handler is None:
        print("Unknown module")
        return None
    
    handler(data)

