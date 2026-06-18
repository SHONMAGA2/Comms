import socket
import json

HOST = '127.0.0.1'
PORT = 6500


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    try:

        s.connect((HOST,PORT))

        while True:

            message = input("Type your message here: ")

            packet = {"module":"TEXT","payload":message}

            s.sendall(
                (json.dumps(packet) + "\n").encode('utf-8')
                )

            data = s.recv(1024)
            response = json.loads(data.decode('utf-8'))
            payload = response.get("payload")

            if not response:
                print("Server closed connection")
                break

            print(f"Response: {payload}")

    except ConnectionRefusedError:
        print("Server not listening")        
