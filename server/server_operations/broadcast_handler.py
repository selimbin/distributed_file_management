import socket
import struct
import threading
import time
class BroadCastHandler:
    def __init__(self, broadcast_group, broadcast_port):
        self.broadcast_group = broadcast_group
        self.broadcast_port = broadcast_port

    def send_broadcast_message(self, message):
        print(f"sending broadcast message: {message}")
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.sendto(message.encode(), (self.broadcast_group, self.broadcast_port))
        broadcast_socket.close()
