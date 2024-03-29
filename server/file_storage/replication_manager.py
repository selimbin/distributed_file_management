# import socket
# from server.server_operations.server_utilities import handle_request
import socket
import time
import uuid


class ReplicationManager:
    def __init__(self, node):
        # self.leader = leader
        # self.backup_servers = servers
        # self.file_manager = file_manager
        self.node = node

    def replicate(self, unique_id, file_name, data, operation):

        if operation == "DELETE":
            self.node.file_manager.delete_file(file_name)
        else:
            self.node.file_manager.replicate(file_name, data.encode())
        print(f"starting replicate: {self.node.servers}")
        try:
            for address in self.node.queue:
                try:
                    retry_count = 0
                    response = None
                    while retry_count <= 3 and not response:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_init:
                            # child_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            # socket_init.connect(address)
                            socket_init.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            socket_init.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                            # Assuming file data is retrieved from the file manager or similar
                            print(f"In replicate to server: {address}")
                            socket_init = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            # with socket.connect(address) as replication_socket:
                            # print("Address in replication: "+str(address))

                            socket_init.connect(address)
                            if operation == "DELETE":
                                socket_init.sendall(f"{unique_id} REPLICATE {file_name} {'!del!'}".encode())
                            elif operation == "EDIT":
                                data2 = self.node.file_manager.read_file(file_name)
                                socket_init.sendall(f"{unique_id} REPLICATE {file_name} {data2}".encode())
                            else:
                                socket_init.sendall(f"{unique_id} REPLICATE {file_name} {data}".encode())

                            response = socket_init.recv(1024).decode()
                            if not response:
                                time.sleep(0.1)
                                retry_count += 1

                    if "successfully" not in response and "REPLICATE" not in response:
                        print(f'RESPONSE during sync: {response}')
                        raise Exception("Child server failed to replicate.")
                    # Expecting an acknowledgment from backup
                    # response = socket_init.recv(1024).decode()
                    # print(f"Replication to {address} successful: {response}")
                    socket_init.close()
                except Exception as e:
                    print(f"Replication Error to {address}: {e}")
        except Exception as e:
            print(f"Replication Error: {e}")
        finally:
            time.sleep(0.2)
            self.node.semaphores.update({file_name: True})

    def parse_critical_data(self, critical_data_str):
        """
        Parse the critical operations data received from a child server.

        Args:
            critical_data_str (str): The critical data received as a string.

        Returns:
            dict: A dictionary with unique IDs as keys and file names as values.
        """
        critical_dict = {}
        if critical_data_str:
            # Split the string by comma to separate each id:file_name pair
            if critical_data_str == "{}":
                return critical_dict
            operations = critical_data_str.split(',')
            for operation in operations:
                if operation:
                    # Split each pair by colon to separate id and file_name
                    unique_id, file_name = operation.strip("{ }").split(':')
                    critical_dict.update({unique_id.strip(" "): file_name.strip(" ")})
        return critical_dict

    def rollback_child_server(self, child_address, critical, last_operations=10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as child_socket:

                retry_count = 0
                child_critical_data = None
                while retry_count <= 3 and not child_critical_data:
                    try:
                        child_socket.connect(child_address)
                        child_socket.sendall("REQUEST_CRITICAL_OPS".encode())
                        child_critical_data = child_socket.recv(1024).decode()
                        # print(f"received critical ops: {child_critical_data}")
                        child_critical = self.parse_critical_data(child_critical_data)
                    except Exception as e:
                        # print(f"Error in leader sending to child: {e}")
                        pass
                    if not child_critical_data:
                        # print(f"No response in rollback, Retry {retry_count + 1} for server {child_address}")
                        time.sleep(0.2)
                        retry_count += 1
                if not child_critical_data:
                    # TODO check this later
                    #  print(f"After {self.max_retries} retries, leader assumes server {child_server} is dead.")
                    #  self.servers.remove(child_server)
                    #  print(f"New child servers available are {self.servers} is dead.")
                    raise Exception(f"{child_address} server is dead")
        except Exception as e:
            print(f"Error while requesting critical operations from child server {child_address}: {e}")
            return False
        # Compare and synchronize
        updated = []
        for unique_id in list(critical.keys())[-last_operations:]:
            file_name = critical.get(unique_id)
            if unique_id not in child_critical and file_name not in updated:
                # Send the file and operation to the child server to synchronize
                try:
                    retry_count = 0
                    response = None
                    while retry_count <= 3 and not response:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as child_socket:
                        # child_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            child_socket.connect(child_address)

                            # Assuming file data is retrieved from the file manager or similar
                            file_data = self.node.file_manager.read_file(file_name)
                            if file_data == 'File not found.':
                                child_socket.sendall(f"{unique_id} REPLICATE {file_name} {'!del!'}".encode())
                            else:
                                if file_data == "":
                                    x = "'"
                                    child_socket.sendall(f"{unique_id} REPLICATE {file_name} {x}".encode())
                                else:
                                    child_socket.sendall(f"{unique_id} REPLICATE {file_name} {file_data}".encode())
                            response = child_socket.recv(1024).decode()
                            if not response:
                                time.sleep(0.1)
                                retry_count += 1
                                # print(f'RESPONSE during sync: {response}')
                    if "successfully" not in response:
                        raise Exception("Child server failed to acknowledge the sync operation.")
                    updated.append(file_name)
                except Exception as e:
                    print(f"Error during critical operation sync for child server {child_address}: {e}")
                    return False

        for unique_id in child_critical.keys():
            file_name = child_critical.get(unique_id)
            if unique_id not in critical.keys() and file_name not in updated:
                try:
                    retry_count = 0
                    response = None
                    while retry_count <= 3 and not response:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as child_socket:
                            child_socket.connect(child_address)
                            file_name = child_critical.get(unique_id)
                            # Assuming file data is retrieved from the file manager or similar
                            file_data = self.node.file_manager.read_file(file_name)
                            new_id = uuid.uuid4()
                            if file_data == 'File not found.':
                                child_socket.sendall(f"{new_id} REPLICATE {file_name} {'!del!'}".encode())
                            else:
                                if file_data == "":
                                    x = "'"
                                    child_socket.sendall(f"{new_id} REPLICATE {file_name} {x}".encode())
                                else:
                                    child_socket.sendall(f"{new_id} REPLICATE {file_name} {file_data}".encode())
                            response = child_socket.recv(1024).decode()
                            if not response:
                                time.sleep(0.1)
                                retry_count += 1
                        if "successfully" not in response:
                            raise Exception("Child server failed to acknowledge the sync operation.")
                        updated.append(file_name)
                except Exception as e:
                    print(f"Error during critical operation sync for child server {child_address}: {e}")
                    return False
        return True

    def initialize(self, address):
        try:
            for file_name, file in self.node.file_manager.all_files():
                unique_id = uuid.uuid4()
                socket_initialization = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_initialization.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                socket_initialization.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                socket_initialization.connect(address)
                if file == "":
                    x = "'"
                    socket_initialization.sendall(f"{unique_id} REPLICATE {file_name} {x}".encode())
                else:
                    socket_initialization.sendall(f"{unique_id} REPLICATE {file_name} {file}".encode())
                # Expecting an acknowledgment from backup
                response = socket_initialization.recv(1024).decode()
            socket_initialization = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_initialization.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_initialization.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            socket_initialization.connect(address)
            socket_initialization.sendall(f"CRITICAL {self.node.critical}".encode())
            print(f"Initialization of data to {address} successful")
        except Exception as e:
            print(f"Initialization Error to {address}: {e}")
