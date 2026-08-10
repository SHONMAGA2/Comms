import socket
from protocol import send_packet, receive_packet
from client_config import SERVER_HOST, SERVER_PORT, DEFAULT_MODULE, SOCKET_TIMEOUT
from handlers import build_handlers, receive_handlers
import threading


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.settimeout(SOCKET_TIMEOUT)

        module_to_be_used = DEFAULT_MODULE
        stop_event = threading.Event()

        def receive_message(s):
            print("Receiver thread started")
            while not stop_event.is_set():
                try:
                    data = receive_packet(s)

                except (ConnectionError, OSError):
                    print("\nConnection to server lost")
                    stop_event.set()
                    break

                if data is None:
                    print("\nServer connection closed")
                    stop_event.set()
                    break

                print(f"Received packet: {data}")

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

        try:
            while not stop_event.is_set():

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

                send_packet(s, packet)

        except KeyboardInterrupt:
            print("\nClosing connection...")
            stop_event.set()

    except ConnectionRefusedError:
        print("Server not listening")

    except socket.timeout:
        print("Connection timed out")

    except ConnectionError as e:
        print(f"Connection error: {e}")