# server/server.py
import socket
import threading
from server.config import SERVER_HOST, SERVER_PORT
from server.file_storage.file_manager import FileManager
from server.server_operations.server_utilities import handle_request

class FileServer:
    def __init__(self):
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.file_manager = FileManager()

    def start(self):
        self.sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client, _ = self.sock.accept()
            threading.Thread(target=self.client_handler, args=(client,)).start()

    def client_handler(self, client_socket):
        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    response = handle_request(data, self.file_manager)
                    client_socket.sendall(response.encode())
                except Exception as e:
                    print(f"Error: {e}")
                    break

if __name__ == '__main__':
    server = FileServer()
    server.start()
