# import socket
# from server.server_operations.server_utilities import handle_request
import socket
import uuid


class ReplicationManager:
    def __init__(self, leader, servers, file_manager):
        self.leader = leader
        self.backup_servers = servers
        self.file_manager = file_manager

    def replicate(self, unique_id, file_name, data, socket):
        for address in self.backup_servers:
            try:
                # with socket.connect(address) as replication_socket:
                # print(str(address))
                socket.connect(address)
                socket.sendall(f"{unique_id} REPLICATE {file_name} {data}".encode())
                # Expecting an acknowledgment from backup
                response = socket.recv(1024).decode()
                print(f"Replication to {address} successful: {response}")
            except Exception as e:
                print(f"Replication Error to {address}: {e}")

    def initialize(self, address):
        try:
            for file_name, file in self.file_manager.all_files():
                unique_id = uuid.uuid4()
                socket_initialization = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_initialization.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                socket_initialization.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                socket_initialization.connect(address)
                socket_initialization.sendall(f"{unique_id} REPLICATE {file_name} {file}".encode())
                # Expecting an acknowledgment from backup
                response = socket_initialization.recv(1024).decode()
            print(f"Initialization of data to {address} successful")
        except Exception as e:
            print(f"Initialization Error to {address}: {e}")
