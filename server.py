import socket
from protocol import send_packet,process_packet
from config import HOST,PORT
from handlers import dispatch_data,routing,clients
import threading

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s :
      s.bind((HOST , PORT))
      s.listen()
      print(f"Server is listening on {HOST}:{PORT}")

      

      def client_thread(conn,addr):
            with conn:
                  print(f"Connected by {addr}")

                  while True:
                              try:
                                    data = process_packet(conn)

                              except (ValueError,TypeError) as e:
                                    print(f"Invalid packet: {e}")
                                    break

                              except ConnectionError as e:
                                    print(f"Connection error: {e}")
                                    break

                              if data is None:
                                    remove_client(conn)
                                    break

                              print(f"RECEIVED: {data}")
                              dispatch_data(conn,data)
                              
                              

                              
                              
                              

                              

      while True:
            conn,addr = s.accept()

            def remove_client(conn):
                  for username, client_conn in clients.items():
                        if client_conn == conn:
                              del clients[username]
                              print(f"{username} disconnected")
                              return

            thread = threading.Thread(
                  target=client_thread,
                  args=(conn,addr)
            )
            thread.start()