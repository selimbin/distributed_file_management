# server/server.py
import asyncio
import socket
import threading
import uuid

from config import SERVER_HOST, SERVER_PORT
from file_storage.file_manager import FileManager
from server_operations.server_utilities import handle_request
from file_storage.replication_manager import ReplicationManager


def parse_request(data):
    unique_id, command, file_name, *content = data.split(maxsplit=3)
    return unique_id, command, file_name, *content


class FileServer:
    def __init__(self):
        self.server_name = str(uuid.uuid4())
        self.host = SERVER_HOST
        self.port = 10006
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.file_manager = FileManager(self.server_name)
        self.servers = [('127.0.0.1', 10006)]
        self.is_leader = False
        self.replication_manager = ReplicationManager(self.is_leader, self.servers, self.file_manager)
        self.request_history = []
        self.queue = [('127.0.0.1', 10006)]
        self.hold_queue = []

    def start(self):
        self.sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client, _ = self.sock.accept()
            if self.is_leader and len(self.servers) != 0 and len(self.queue) != 0:
                server_queue = self.queue.pop(0)
                threading.Thread(target=self.client_handler, args=(client, server_queue)).start()
                self.queue.append(server_queue)
            else:
                if self.is_leader and len(self.servers) > 1:
                    print(f"Adding to hold queue")
                    self.hold_queue.append(client)
                else:
                    threading.Thread(target=self.client_handler, args=(client, 'None')).start()
            if len(self.hold_queue) > 0 and len(self.queue) > 0:
                server_queue = self.queue.pop(0)
                threading.Thread(target=self.client_handler, args=(client, server_queue)).start()

    def client_handler(self, client_socket, child_server):
        with client_socket:
            try:
                data = client_socket.recv(1024).decode()
                unique_id, operation, file_name, file_data = parse_request(data)
                print(f"Parse Results: {unique_id}, {operation}, {file_name}, {file_data}")
                if unique_id in self.request_history:
                    response = "operation already executed"
                    client_socket.sendall(response.encode())
                    return
                if self.is_leader and child_server != 'None':
                    print(f"Sending request from leader to server: {str(child_server)}")
                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    new_socket.connect(child_server)
                    new_socket.sendall(data.encode())
                    # Expecting an acknowledgment from backup
                    response = new_socket.recv(1024).decode()
                    if operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        _, operation, file_name, file_data = parse_request(data)
                        if operation == "REPLICATE":
                            response = handle_request(response, self.file_manager)
                            socket_replication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            print("Starting replication manager")
                            # command, *content = data.split(maxsplit=3)
                            # TODO: Check if we should replace how we use replication manager to give it response data
                            self.replication_manager.replicate(unique_id, file_name, file_data, socket_replication)
                        else:
                            response = operation + " operation failed"
                else:
                    response = handle_request(data, self.file_manager)
                    if not self.is_leader and operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        # socket_replication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        if "successfully" in response:
                            # print("Will start replication manager")
                            response = unique_id + " REPLICATE " + file_name + " " + file_data
                            # self.replication_manager.replicate(unique_id, file_name, file_data, operation, socket_replication)
                self.request_history.append(unique_id)
                client_socket.sendall(response.encode())
            except Exception as e:
                print(f"Error: {e}")


if __name__ == '__main__':
    server = FileServer()
    server.start()
