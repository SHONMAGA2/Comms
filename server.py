import socket
from protocol import send_packet,process_packet
from config import HOST,PORT,SOCKET_TIMEOUT
from handlers import dispatch_data,routing,clients
import threading

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s :
      s.bind((HOST , PORT))
      s.listen()
      print(f"Server is listening on {HOST}:{PORT}")

      def client_thread(conn,addr):
            with conn:
                  conn.settimeout(SOCKET_TIMEOUT)
                  print(f"Connected by {addr}")

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

                              dispatch_data(conn,data)
                              

                              
                              
                              

                              

      while True:
            conn,addr = s.accept()

            thread = threading.Thread(
                  target=client_thread,
                  args=(conn,addr)
            )
            thread.start()