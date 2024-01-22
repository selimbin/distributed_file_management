# import socket
# from server.server_operations.server_utilities import handle_request


class ReplicationManager:
    def __init__(self, leader, servers, file_manager):
        self.leader = leader
        self.backup_servers = servers
        self.file_manager = file_manager

    def replicate(self, unique_id, file_name, data, socket):
        for address in self.backup_servers:
            try:
                # with socket.connect(address) as replication_socket:
                print(str(address))
                socket.connect(address)
                socket.sendall(f"{unique_id} REPLICATE {file_name} {data}".encode())
                # Expecting an acknowledgment from backup
                response = socket.recv(1024).decode()
                print(f"Replication to {address} successful: {response}")
            except Exception as e:
                print(f"Replication Error to {address}: {e}")
