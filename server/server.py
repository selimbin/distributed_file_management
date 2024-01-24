# server/server.py
import asyncio
import socket
import threading
import time
import uuid

from config import SERVER_HOST, SERVER_PORT, MAX_RETRIES, RETRY_DELAY, HEARTBEAT_TIME, BROADCAST_PORT, BROADCAST_GROUP
from file_storage.file_manager import FileManager
from server_operations.broadcast_handler import BroadCastHandler
from server_operations.election_handler import ElectionHandler
from server_operations.server_utilities import handle_request
from file_storage.replication_manager import ReplicationManager


def parse_request(data):
    unique_id, command, file_name, *content = data.split(maxsplit=3)
    return unique_id, command, file_name, *content


def send_message(port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', port))
        client_socket.send(message.encode())
    except ConnectionRefusedError:
        pass
    finally:
        client_socket.close()


def broadcast_presence(rank, port, broadcast_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f'NEW_NODE:{rank}:{port}'.encode()
        sock.sendto(message, ('<broadcast>', broadcast_port))
        print(f"new node sending broad_cast_message")


class FileServer:
    def __init__(self):
        self.server_name = uuid.uuid4()
        self.rank = int(self.server_name)
        self.host = SERVER_HOST
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        self.heartbeat_time = HEARTBEAT_TIME
        self.port = 10006
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_manager = FileManager(str(self.server_name))
        self.servers = []
        self.is_leader = False

        self.leader = None
        self.replication_manager = ReplicationManager(self.is_leader, self.servers, self.file_manager)
        # self.request_history = []
        self.queue = []
        self.hold_queue = []
        self.history = {}
        self.semaphores = {}
        self.in_process = []
        self.broadcast_port = BROADCAST_PORT
        self.broadcast_group = BROADCAST_GROUP
        self.broadcast_handler = BroadCastHandler(self.broadcast_group, self.broadcast_port)
        self.election_handler = ElectionHandler(self, self.servers)
        self.election_event = threading.Event()

        self.raised = False

    def start(self):
        sock = self.sock
        sock.bind((self.host, self.port))
        sock.listen()
        threading.Thread(target=server.listen_for_broadcasts, daemon=True).start()

        print("before")
        # self.wait_for_leader_ack()
        threading.Thread(target=self.wait_for_leader_ack, daemon=True).start()
        print(f"Server listening on {self.host}:{self.port}")
        threading.Thread(target=self.heartbeat).start()
        while True:
            client, _ = sock.accept()
            if self.is_leader and len(self.servers) > 1 and len(self.queue) == 0:
                self.hold_queue.append(client)
            else:
                # threading.Thread(target=self.handle_incoming, args=(client,)).start()
                pass

            if len(self.hold_queue) > 0 and len(self.queue) > 0:
                # threading.Thread(target=self.handle_incoming, args=(client,)).start()
                pass

    def listen_for_broadcasts(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_socket.bind(('', self.broadcast_port))
        while True:
            try:
                message, _ = broadcast_socket.recvfrom(1024)
                print(f"Node {self.rank} received broadcast message: {message}")
                print(f"decoding broadcast: {message.decode()}")
                data = message.decode().split(':')
                print("here:" + data[1])
                if int(data[1]) != self.rank:
                    self.handle_broadcast_message(message.decode())
            except Exception as e:
                print(f"Node {self.rank} error receiving broadcast message: {e}")

    def handle_broadcast_message(self, message):
        print("handling new broadcast message")
        data = message.split(':')
        print(f"Leader: {self.is_leader}")
        if data[0] == 'NEW_NODE' and self.is_leader:
            new_node_rank = int(data[1])
            new_node_port = int(data[2])
            new_node_info = {'rank': new_node_rank, 'port': new_node_port}
            if new_node_info not in self.servers:
                self.servers.append(new_node_info)
                print(f"Leader Node {self.rank} acknowledging new Node {new_node_rank}.")
                send_message(new_node_port, f'ACK_LEADER:{self.rank}')

    def wait_for_leader_ack(self, timeout=10):
        print(f"new node waiting for leader ack")
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < timeout:
            if self.leader is not None:
                print(f"Node {self.rank}: Acknowledged by leader Node {self.leader}.")
                return
            # time.sleep(1)

        # No leader response within timeout
        print(f"Node {self.rank}: No response from leader. Checking for higher-ranked nodes.")
        # if not any(n['rank'] > self.rank for n in self.servers):
        print(f"new node declaring victory")
        # self.election_handler.declare_victory()
        self.is_leader = True
        self.leader = self.rank
        # Notify other nodes of victory
        self.broadcast_handler.send_broadcast_message(f'VICTORY:{self.rank}')
        # self.election_event.set()
        # b.c he is leader
        # else:
        #     self.election_handler.start_election()

    def heartbeat(self):
        start_time = time.perf_counter()
        while True:
            if self.is_leader:
                if time.perf_counter() - start_time > 10:
                    # print(f"Performing Heartbeat on Children Servers")
                    # perform heartbeat
                    for address in self.queue:
                        retry_count = 0
                        response = None
                        while retry_count <= self.max_retries and not response:
                            # print(f"in while: {retry_count}")
                            try:
                                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                new_socket.connect(address)
                                new_socket.sendall("HEARTBEAT".encode())
                                response = new_socket.recv(1024).decode()
                            except Exception as e:
                                pass
                            if not response:
                                # print(f"No Heartbeat, Retry {retry_count + 1} for server {address}")
                                time.sleep(self.retry_delay)
                                retry_count += 1
                        if not response:
                            print(f"After {self.max_retries} HEARTBEATS, leader assumes server {address} is dead.")
                            self.servers.remove(address)
                            self.queue.remove(address)
                            print(f"New child servers available are {self.servers}.")
                    start_time = time.perf_counter()
                    # print("Completed Heartbeats on servers")

            else:
                if time.perf_counter() - start_time > 10 and self.leader is None == False:
                    print(f"Performing Heartbeat on Leader")
                    retry_count = 0
                    response = None
                    while retry_count <= self.max_retries and not response:
                        try:
                            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            new_socket.connect(self.leader)
                            new_socket.sendall("HEARTBEAT".encode())
                            response = new_socket.recv(1024).decode()
                        except Exception as e:
                            pass
                        if not response:
                            print(f"No Heartbeat, Retry {retry_count + 1} for Leader {self.leader}")
                            time.sleep(self.retry_delay)
                            retry_count += 1
                    if not response:
                        print(f"After {self.max_retries} HEARTBEATS leader is assumed dead, Launching leader election.")
                        self.servers.remove(self.leader)
                    else:
                        print("Completed heartbeat, Leader is alive")
                        # Start leader election here
                    start_time = time.perf_counter()

    def handle_incoming(self, client):
        try:
            data = client.recv(1024).decode()
        except Exception as e:
            print(f"Error while receiving data: {e}")
            return
        if data == "HEARTBEAT":
            print(f"Received heartbeat request from server {client}")
            client.sendall("ACKNOWLEDGING HEARTBEAT".encode())
            return

        unique_id, _, _, _ = parse_request(data)
        if unique_id not in self.in_process:
            completed = False
            while not completed:
                try:
                    if self.is_leader and len(self.servers) != 1 and len(self.queue) != 0:
                        server_queue = self.queue.pop(0)
                        # threading.Thread(target=self.client_handler, args=(client, server_queue)).start()
                        self.client_handler(client, server_queue, data)
                        self.queue.append(server_queue)
                        completed = True
                    else:
                        if self.is_leader and len(self.servers) > 1:
                            self.hold_queue.append(client)
                            completed = True
                        else:
                            # threading.Thread(target=self.client_handler, args=(client, 'None')).start()
                            self.client_handler(client, 'None', data)
                            completed = True
                except Exception as e:
                    print(e)
                    completed = False
        else:
            if unique_id in self.history.keys():
                try:
                    client.sendall(self.history.get(unique_id).encode())
                except Exception as e:
                    print(f"Error {e} , Issue in sending response to client or server.")
            else:
                print(
                    f"Request {unique_id} is still being processed.")  # Should we include this in client implementation?

    def client_handler(self, client_socket, child_server, data):
        try:
            with client_socket:
                unique_id, operation, file_name, file_data = parse_request(data)
                print(f"Parse Results: {unique_id}, {operation}, {file_name}, {file_data}")
                if unique_id in self.history.keys():
                    response = self.history.get(unique_id)
                    try:
                        client_socket.sendall(response.encode())
                    except Exception as e:
                        print(f"Error {e} , Issue in sending response to client or server.")
                    return
                self.in_process.append(unique_id)
                if file_name not in self.semaphores.keys():
                    self.semaphores.update({file_name: True})
                if operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                    if self.semaphores.get(file_name):
                        self.semaphores.update({file_name: False})
                    else:
                        raise Exception(f"Semaphore for file {file_name} is taken")

                if self.is_leader and child_server != 'None':
                    print(f"Sending request from leader to server: {str(child_server)}")
                    retry_count = 0
                    response = None
                    while retry_count <= self.max_retries and not response:
                        try:
                            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            new_socket.connect(child_server)
                            new_socket.sendall(data.encode())
                            response = new_socket.recv(1024).decode()
                        except Exception as e:
                            pass
                        if not response:
                            print(f"No response, Retry {retry_count + 1} for server {child_server}")
                            time.sleep(self.retry_delay)
                            retry_count += 1
                    if not response:
                        print(f"After {self.max_retries} retries, leader assumes server {child_server} is dead.")
                        self.servers.remove(child_server)
                        print(f"New child servers available are {self.servers} is dead.")
                        raise Exception(f"{child_server} server is dead")

                    if operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        _, operation2, file_name, file_data = parse_request(data)
                        if operation2 == "REPLICATE":
                            response = handle_request(response, self.file_manager)
                            socket_replication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            print("Starting replication manager")
                            # command, *content = data.split(maxsplit=3)
                            self.replication_manager.replicate(unique_id, file_name, file_data, socket_replication)
                        else:
                            response = operation + " operation failed"
                else:
                    response = handle_request(data, self.file_manager)
                    if not self.is_leader and operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        # socket_replication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        if "successfully" in response:
                            response = unique_id + " REPLICATE " + file_name + " " + file_data

                self.history.update({unique_id: response})
                try:
                    client_socket.sendall(response.encode())
                except Exception as e:
                    print(f"Error {e} , Issue in sending response to client or server.")

                # self.request_history.append(unique_id)
                if child_server != 'None':
                    self.queue.append(child_server)
        except Exception as e:
            raise e


if __name__ == '__main__':
    server = FileServer()
    threading.Thread(target=broadcast_presence, args=(int(server.server_name), server.port, server.broadcast_port),
                     daemon=True).start()
    # threading.Thread(target=server.listen_for_broadcasts(), daemon=True).start()
    # print("here2")
    # server.wait_for_leader_ack()
    server.start()
