import socket
from protocol import send_packet,process_packet
from server_config import HOST,PORT,DEFAULT_MODULE,SOCKET_TIMEOUT
from handlers import build_handlers,dispatch_data
import threading


with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s :
      s.bind((HOST , PORT))
      s.listen()
      print(f"Server is listening on {HOST}:{PORT}")

      clients = []

      def broadcast(packet,sender):
            for client in clients.copy():
                  if client is not sender:
                        continue
            try:
                  send_packet(client,packet)
            except ConnectionError:
                  print("Could not send to client")


      
      def handle_client(conn,addr):
            print(f"Connected by {addr}")
            print(f"Connected clients: {len(clients)}")
            conn.settimeout(SOCKET_TIMEOUT)
            module_to_be_used = DEFAULT_MODULE
            try:
                  with conn:
                        while True:
                              try:
                                    data = process_packet(conn)
                              
                              except socket.timeout:
                                    print("Connection timed out")
                                    break
                              
                              except (ValueError,TypeError) as e:
                                    print(f"Invalid packet: {e}")
                                    break
                              
                              except ConnectionError as e:
                                    print(f"Connection error: {e}")
                                    break
                              
                              if data is None:
                                    break
                              
                              dispatch_data(data)
                              broadcast(data,conn)
                              

            finally:
                  if conn in clients:
                        clients.remove(conn)

                  print(f"Disconnected: {addr}")
                  print(f"Connected clients: {len(clients)}")

      while True:
            conn,addr = s.accept()
            clients.append(conn)
            
            thread = threading.Thread(
                  target = handle_client,
                  args = (conn,addr)
            )

            thread.start()