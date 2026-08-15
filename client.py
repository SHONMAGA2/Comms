import socket
from protocol import send_packet,receive_packet
from config import HOST,PORT,DEFAULT_MODULE
from handlers import build_handlers,dispatch_data
import threading

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST,PORT))

        module_to_be_used = DEFAULT_MODULE
        client_list = []
        client_list_lock = threading.Lock()
        client_list_ready = threading.Event()

        def receiver_thread(sock):
            while True:
                data = receive_packet(sock)


                if data is None:
                    print("server connection closed")
                    break

                print("CLIENT RECEIVED:", data)

                module_name = data.get("module")
                data_type = data.get("type")

                if module_name == "TEXT" and data_type == "MESSAGE":
                    print(f"{data.get("sender")}: {data.get("payload")}")

                elif module_name == "SYSTEM" and data_type == "CLIENT_LIST":
                    with client_list_lock:
                        client_list.clear()
                        client_list.extend(data.get("payload", []))

                    client_list_ready.set()

                elif module_name == "SYSTEM" and data_type == "ERROR":
                    print(data.get("payload"))

                else:
                    print("Unknown packet type")

        thread = threading.Thread(
            target=receiver_thread,
            args=(s,)
        )

        thread.start()

        username = input("Type your Username: ")
        auth_builder = build_handlers.get("AUTH")
        packet = auth_builder(username)
        send_packet(s,packet)
                
        while True:
            print("available commands: /conn -> list and select users you can talk to")
            message = input("> ")

            if message.startswith("/conn"):

                client_list_ready.clear()

                client_list_builder = build_handlers["SYSTEM"]["type"]["CLIENT_LIST"]
                packet = client_list_builder(message)
                send_packet(s,packet)

                if not client_list_ready.wait(timeout=5):
                    print("Server did not respond with a client list")
                    continue

                with client_list_lock:
                    users = list(client_list)

                users = [
                    user for user in users
                    if user != username
                ]

                if not users:
                    print("No other users are currently connected.")
                    continue

                print(f"Connected users: \n")

                for number, user in enumerate(users,1):
                    print(f"{number}. {user}")

                try:
                    choice = int(input("Select user > "))
                except ValueError:
                    print("please enter a number")
                    continue

                if choice < 1 or choice > len(users):
                    print("Invalid selection")
                    continue

                recipient = users[choice - 1]

                message = input(f"Message to {recipient} > ")

                text_builder = build_handlers.get("TEXT")
                packet = text_builder(message,username,recipient)
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