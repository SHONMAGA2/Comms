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


      def handle_client(conn,addr):
            print(f"Connected by {addr}")
            print(f"Connected clients: {len(clients)}")
            conn.settimeout(SOCKET_TIMEOUT)
            module_to_be_used = DEFAULT_MODULE

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
                                          
                        message = input("> ")
                              
                        if message.startswith("/module"):
                              module_to_be_used = message.split(maxsplit=1)[1]
                              print(f"switched to {module_to_be_used}")
                              continue                        
                              
                        builder = build_handlers.get(module_to_be_used)
                                                                                          
                        if builder is None:
                              print("Unknown module")
                              continue
                                                                                          
                        packet = builder(message)            
                                                                                          
                        try:
                              send_packet(conn, packet)
                              
                        except socket.timeout:
                              print("Connection timed out while sending")
                              break
                              
                        except ConnectionError as e:
                              print(f"Connection error while sending: {e}")
                              break

      while True:
            conn,addr = s.accept()
            clients.append(conn)
            
            thread = threading.Thread(
                  target = handle_client,
                  args = (conn,addr)
            )

            thread.start()