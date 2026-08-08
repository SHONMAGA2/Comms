import socket
from protocol import send_packet,receive_packet
from config import HOST,PORT,DEFAULT_MODULE,SOCKET_TIMEOUT
from handlers import build_handlers,receive_handlers

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:

        s.connect((HOST,PORT))
        s.settimeout(SOCKET_TIMEOUT)

        module_to_be_used = DEFAULT_MODULE
        while True:

            message = input("> ")

            if message.startswith("/module"):
                module_to_be_used = message.split(maxsplit=1)[1]
                print(f"switched to {module_to_be_used}")


                if module_to_be_used == "SYSTEM":
                    builder = build_handlers.get("SYSTEM")

                if builder is None:
                    print("Unknown module")
                    continue

                packet = builder()
                send_packet(s,packet)

                continue

            builder = build_handlers.get(module_to_be_used)

            if builder is None:
                print("Unknown module")
                continue

            packet = builder(message)            

            send_packet(s,packet)
            
            data = receive_packet(s)

            if data is None:
                print("server connection closed ")
                break

            module_name = data.get("module")

            handler = receive_handlers.get(module_name)

            if handler is None:
                print("Unknown module")
                continue

            handler(data)


    except ConnectionRefusedError:
        print("Server not listening")

    except socket.timeout:
        print("Connection timed out")

    except ConnectionError as e:
        print(f"Connection error: {e}")