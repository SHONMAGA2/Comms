import socket
import json
import struct
import platform

HOST = '127.0.0.1'
PORT = 6500

system_info = {
      "hostname":socket.gethostname(),
      "platform":platform.system(),
            "release":platform.release()
}

def send_message(module_type,message):

      packet = {"module":"TEXT","payload":message}

      payload = json.dumps(packet).encode('utf-8')

      packet_length = len(payload)
      header = struct.pack("!I",packet_length)

      conn.sendall(header + payload)

def recv_exact(sock,size):
      data = b""

      while len(data) < size:
            chunk = sock.recv(size - len(data))

            if not chunk:
                  return None

            data += chunk

      return data

def text_handler(packet):
                  
      payload = packet.get("payload")
      print(f"Response: {payload}")

def system_handler(packet):
      print("Client System info")
      hostname = system_info.get("hostname")
      platform = system_info.get("platform")
      release = system_info.get("release")

      print(f"Hostname: {hostname}",f"Platform: {platform}",f"Release: {release}")      

modules = {
      "TEXT":text_handler,
      "SYSTEM":system_handler
}

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s :
      s.bind((HOST , PORT))
      s.listen()
      print(f"Server is listening on {HOST}:{PORT}")

      while True:
            conn,addr = s.accept()
            with conn:
                  print(f"Connected by {addr}")

                  module_to_be_used = input("module: ")

                  while True:
                              header = recv_exact(conn,4)

                              if header is None:
                                    print("No header was found")
                                    conn.close()

                              length = struct.unpack("!I",header)[0]

                              MAX_PACKET_LENGTH = 1024 * 1024

                              if length >  MAX_PACKET_LENGTH:
                                    print("packet length too large ")
                                    conn.close()
                                    break

                              payload = recv_exact(conn,length)

                              data = json.loads(payload.decode('utf-8'))

                              module_name = data.get("module")

                              handler = modules.get(module_name)

                              if handler:
                                    handler(data)
                              else:
                                    print("unknown module")
            
                              message = input("> ")

                              if message.startswith("/module"):
                                    module_to_be_used = message.split(maxsplit=1)[1]
                                    print(f"switched to {module_to_be_used}")
                                    continue

                              send_message(module_to_be_used,message)