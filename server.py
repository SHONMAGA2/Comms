import socket
import json

HOST = '127.0.0.1'
PORT = 6500

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s :
    s.bind((HOST , PORT))
    s.listen()
    print(f"Server is listening on {HOST}:{PORT}")

    while True:
        conn,addr = s.accept()
        with conn:
            print(f"Connected by {addr}")

            while True:
                    try:

                        data = conn.recv(1024)

                        if not data:
                            break

                        response = json.loads(data.decode('utf-8'))
                        module = response.get("module")
             
                        if module == "TEXT":

                            payload = response.get("payload")
                            print(f"Recieved: {payload}")
                            
                            message = input("Type your response here: ")
                            packet = {"module":"TEXT","payload":message}

                            conn.sendall((json.dumps(packet) + "\n").encode('utf-8'))


                        elif module is None:
                            print("Packet missing module")
                            continue

                    except json.JSONDecodeError as e:
                        print(f"Invalid JSON: {e}")
                        continue

                    except KeyError:
                        print("Missing 'module' key in packet")       

                
            