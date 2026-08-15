import socket
from protocol import send_packet,receive_packet
from config import HOST,PORT,DEFAULT_MODULE
from handlers import build_handlers,dispatch_data
import threading

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST,PORT))

        module_to_be_used = DEFAULT_MODULE
        def receiver_thread(sock):
            while True:
                data = receive_packet(sock)

                if data is None:
                    print("server connection closed")
                    break

                dispatch_data(sock,data)

        thread = threading.Thread(
            target=receiver_thread,
            args=(s,)
        )

        thread.start()

                
        while True:

            username = input("Type your Username: ")
            auth_builder = build_handlers.get("AUTH")
            packet = auth_builder(username)
            send_packet(s,packet)

            print("available commands: /conn -> list and select users you can talk to")

            message = input("> ")
            

            if message.startswith("/conn"):
                client_list_builder = build_handlers["SYSTEM"]["type"]["CLIENT_LIST"]
                packet = client_list_builder(message)
                send_packet(s,packet)
                continue

            builder = build_handlers.get(module_to_be_used)

            if builder is None:
                print("Unknown module")
                continue

            packet = builder(message)
            send_packet(s,packet)



    except ConnectionRefusedError:      
        print("Server not listening")

    except ConnectionError as e:
        print(f"Connection error: {e}")