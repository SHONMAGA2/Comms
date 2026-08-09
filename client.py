import socket
from protocol import send_packet,receive_packet
from client_config import SERVER_HOST,SERVER_PORT,DEFAULT_MODULE,SOCKET_TIMEOUT
from handlers import build_handlers,receive_handlers
import threading

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:

        s.connect((SERVER_HOST,SERVER_PORT))
        s.settimeout(SOCKET_TIMEOUT)

        module_to_be_used = DEFAULT_MODULE

        def receive_message(s):
            while True:
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

        thread = threading.Thread(
                    target=receive_message,
                    args=(s,)
                )
        thread.start()
                
        
        while True:

            message = input("> ")

            if message.startswith("/module"):
                module_to_be_used = message.split(maxsplit=1)[1]
                print(f"switched to {module_to_be_used}")
                continue

            builder = build_handlers.get(module_to_be_used)

            if builder is None:
                print("Unknown module")
                continue


            if module_to_be_used == "SYSTEM":
                packet = builder()
            else:
                packet = builder(message)            

            send_packet(s,packet)
            

    except ConnectionRefusedError:
        print("Server not listening")

    except socket.timeout:
        print("Connection timed out")

    except ConnectionError as e:
        print(f"Connection error: {e}")