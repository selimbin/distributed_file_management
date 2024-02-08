# server/server.py
# import asyncio
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


def broadcast_presence(rank, port, broadcast_port, ip):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f'NEW_NODE:{rank}:{ip}:{port}'.encode()
        sock.sendto(message, ('<broadcast>', broadcast_port))
        print(f"new node sending broad_cast_message")
        sock.close()


class FileServer:
    def __init__(self):
        self.server_name = uuid.uuid4()
        self.rank = int(self.server_name)
        self.host = '172.20.10.5'
        # self.host = '127.0.0.1'
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        self.heartbeat_time = HEARTBEAT_TIME
        self.broadcast_ip = '255.255.224.0'
        self.port = 10005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_manager = FileManager(str(self.server_name))
        self.servers = {}
        self.is_leader = False
        self.leader_rank = None
        self.is_active = True
        self.leader = None
        self.queue = []
        self.replication_manager = ReplicationManager(self.is_leader, self.queue, self.file_manager)
        # self.request_history = []

        self.hold_queue = []
        self.history = {}
        self.semaphores = {}
        self.in_process = []
        self.broadcast_port = BROADCAST_PORT
        self.broadcast_group = BROADCAST_GROUP
        self.broadcast_handler = BroadCastHandler(self.broadcast_group, self.broadcast_port)
        self.election_handler = ElectionHandler(self)
        self.election_event = threading.Event()

        # self.critical = {'dsughsdfiuhd': 'testfile_copy.txt'}
        self.critical = {}

        self.raised = False
    def test_election(self):
        time.sleep(20)
        print(f"testing leader election")
        self.election_handler.start_election()

    def test_2(self):
        while True:
            print(f"\nLeader rank : {self.leader_rank}, {self.leader} and flag leader is {self.is_leader}")
            if self.is_leader:
                print(f"Leader servers are: {self.servers.values()} and queue is: {self.queue}")
            print("\n")
            time.sleep(15)

    def start(self):
        sock = self.sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind((self.host, self.port))
        sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
        threading.Thread(target=self.heartbeat).start()
        # threading.Thread(target=self.test_election).start()
        threading.Thread(target=self.test_2).start()
        while True:
            client, _ = sock.accept()
            # if self.is_leader and len(self.servers) > 1:
            #     self.hold_queue.append(client)
            # else:
            threading.Thread(target=self.handle_incoming, args=(client,)).start()
                # pass

            if len(self.hold_queue) > 0 and len(self.queue) > 0:
                threading.Thread(target=self.handle_incoming, args=(client,)).start()
                pass

    def send_message(self, host, port, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with client_socket:
                # print(f"Here: {(host, port)}")
                client_socket.connect((host, port))

                client_socket.sendall(message.encode())
        except Exception as e:
            print(f"Error in send message : {e}")
            pass
        finally:
            client_socket.close()
            return

    def listen_for_broadcasts(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        broadcast_socket.bind(('', self.broadcast_port))
        while True:
            try:
                message, _ = broadcast_socket.recvfrom(1024)
                print(f"Node {self.rank} received broadcast message: {message}")
                # print(f"decoding broadcast: {message.decode()}")
                data = message.decode().split(':')
                # print(f"here in :" + data[0] + " : " + data[1])
                if "CLIENT" in data[0]:
                    print(f"Node {self.rank} received broadcast message: {message}")
                    self.handle_broadcast_message(message.decode())
                elif "LEADER_AT" not in data[0] and int(data[1]) != self.rank:
                    print(f"Node {self.rank} received broadcast message: {message}")
                    self.handle_broadcast_message(message.decode())
            except Exception as e:
                print(f"Node {self.rank} error receiving broadcast message: {e}")

    def handle_broadcast_message(self, message):
        print(f"data: {message}")
        data = message.split(':')
        # print(f"Leader: {self.is_leader}: message is : {data}")
        if data[0] == 'NEW_NODE' and self.is_leader:
            print("handling new broadcast message")
            new_node_rank = int(data[1])
            new_node_ip = data[2]
            new_node_port = int(data[3])
            new_node_info = (new_node_ip, new_node_port)
            if new_node_rank not in self.servers.keys():
                try:
                    print(f'Initializing new server')
                    self.replication_manager.initialize(new_node_info)
                    self.servers.update({new_node_rank: new_node_info})
                    self.queue.append(new_node_info)
                except Exception as e:
                    print(f"Error during initialization of new server: {e}")
                print(f"Leader Node {self.rank} acknowledging new Node {new_node_rank}.")
                self.send_message(new_node_ip, new_node_port, f'ACK_LEADER:{self.rank}:{self.host}:{self.port}|{self.servers}')
        elif data[0] == 'VICTORY':
            new_node_rank = int(data[1])
            new_node_ip = data[2]
            new_node_port = int(data[3])
            new_node_info = (new_node_ip, new_node_port)
            if new_node_rank > self.rank:
                print(f"New leader from broadcast: {new_node_info}")
                self.leader = new_node_info
                self.leader_rank = new_node_rank
                self.is_leader = False
            elif new_node_rank < self.rank:
                self.election_handler.start_election()
        elif data[0] == 'CLIENT':
            # print(f"in client: {data}")
            # new_node_ip = data[1]
            # new_node_port = int(data[2])
            # self.send_message(new_node_ip, new_node_port, f'LEADER_AT:{self.leader[0]}:{self.leader[1]}')
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    message = f"LEADER_AT:{str(self.leader[0])}:{self.leader[1]}".encode()
                    sock.sendto(message, ('<broadcast>', self.broadcast_port))
                    # print(f"new node sending broad_cast_message")
                    sock.close()
            except Exception as e:
                print(f"error sending broadcast: {e}")

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
        self.servers.update({self.rank: (self.host, self.port)})
        self.leader = (self.host, self.port)
        # Notify other nodes of victory
        count = 0
        while count <= 3:
            self.broadcast_handler.send_broadcast_message(f'VICTORY:{self.rank}:{self.host}:{self.port}')
            count += 1
            time.sleep(0.1)

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
                    temp_servers = self.servers.copy()
                    removed = False
                    servers = self.servers.copy().keys()
                    for rank in servers:
                        if rank != self.rank:
                            retry_count = 0
                            response = None
                            address = self.servers.get(rank)
                            while retry_count <= self.max_retries and not response:
                                # print(f"Performing Heartbeat on Child Server {rank}")
                                try:
                                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    new_socket.connect(address)
                                    new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                    new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                                    new_socket.sendall(f"HEARTBEAT:{self.rank}:{self.host}:{self.port}".encode())
                                    response = new_socket.recv(1024).decode()
                                    new_socket.close()
                                except Exception as e:
                                    pass
                                if not response:
                                    print(f"No Heartbeat, Retry {retry_count + 1} for server {rank} at address: {address}")
                                    time.sleep(self.retry_delay)
                                    retry_count += 1
                            if not response:
                                print(f"After {self.max_retries} HEARTBEATS, leader assumes server {rank} at address {address} is dead.")
                                info = self.servers.get(rank)
                                temp_servers.pop(rank)
                                if info in self.queue:
                                    self.queue.remove(info)
                                removed = True
                    self.servers = temp_servers.copy()
                    if removed:
                        print(f"New child servers available are {self.servers}.")
                    start_time = time.perf_counter()
            else:
                if time.perf_counter() - start_time > 10 and self.leader and not self.is_leader:
                    # print(f"Performing Heartbeat on Leader")
                    retry_count = 0
                    response = None
                    leader = self.leader
                    while retry_count <= self.max_retries and not response:
                        try:
                            # print(f"sending heartbeat to leader at {self.leader}")
                            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            new_socket.connect(self.leader)
                            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                            new_socket.sendall(f"HEARTLEADER:{self.rank}:{self.host}:{self.port}".encode())
                            response = new_socket.recv(1024).decode()
                            new_socket.close()
                        except Exception as e:
                            print(f"error sending heartbeat to leader:{e}")
                            pass
                        if not response:
                            print(f"No Heartbeat, Retry {retry_count + 1} for Leader {leader}")
                            time.sleep(self.retry_delay)
                            retry_count += 1
                    if not response:
                        print(f"After {self.max_retries} HEARTBEATS leader is assumed dead, Launching leader election.")
                        if leader in self.servers.keys():
                            self.servers.pop(self.leader_rank)
                        # self.election_handler.start_election()
                        threading.Thread(target=self.election_handler.start_election).start()
                    # else:
                        # print("Completed heartbeat, Leader is alive")
                    start_time = time.perf_counter()

    def handle_incoming(self, client):
        try:
            data = client.recv(1024).decode()
        except Exception as e:
            print(f"Error while receiving data: {e}")
            return
        # print(f"incoming data: {data}")
        if data.startswith("HEARTLEADER"):
            # print("Here 1")
            if self.is_leader:
                heart_rank = int(data.split(':')[1])
                heart_address = (data.split(':')[2], int(data.split(':')[3]))
                # print(f"Here 2: {heart_address}")
                if heart_rank not in self.servers.keys():
                    self.servers.update({heart_rank: heart_address})
                if heart_address not in self.queue:
                    try:
                        print(f"Starting rollback on server {heart_address}")
                        self.replication_manager.rollback_child_server(heart_address, self.critical)
                        self.queue.append(heart_address)
                    except Exception as e:
                        print(f"Error in rollback: {e}")
                client.sendall("ACKNOWLEDGING HEARTBEAT".encode())
                return
            else:
                # heart_rank = int(data.split(':')[1])
                self.election_handler.start_election()
                return
        elif data.startswith("HEARTBEAT"):
            # print("Here 3")
            # print(f"Received heartbeat request from server {client}")
            client.sendall("ACKNOWLEDGING HEARTBEAT".encode())
            return
        elif data.startswith('REQUEST_CRITICAL_OPS'):
            client.sendall(f"{self.critical}".encode())
            return
        elif data.startswith('ELECTION'):
            print(f"Received 'ELECTION'")
            threading.Thread(target=self.election_handler.start_election).start()
            # print(f"Staring an election from pos 1.")
        elif data.startswith('VICTORY'):
            leader_rank = int(data.split(':')[1])
            # print(f"{leader_rank}  >  {self.leader_rank}")
            if leader_rank > self.rank:
                self.leader = (data.split(':')[2], int(data.split(':')[3]))
                if self.leader in self.queue:
                    self.queue.remove(self.leader)
                self.servers.update({self.leader_rank: self.leader})
                print(f"New leader at {self.leader}")
                self.election_event.set()
            else:
                if leader_rank < self.rank:
                    # print(f"Staring an election from pos 2.")
                    self.election_handler.start_election()
        elif data.startswith('ACK_LEADER'):
            data_2 = data.split('|')[0]
            self.leader_rank = int(data_2.split(':')[1])
            self.leader = (data_2.split(':')[2], int(data_2.split(':')[3]))
            if self.leader in self.queue:
                self.queue.remove(self.leader)
            data_3 = data.split('|')[1].strip("[] ")
            for x in data_3.split("),"):
                rank_loop = int(x.split(":")[0].strip(" {}"))
                host_loop = x.split(":")[1].strip("() ").split(",")[0].strip(" '""")
                port_loop = int(x.split(":")[1].strip("() ").split(",")[1].strip(" )}{"))
                self.servers.update({rank_loop: (host_loop, port_loop)})
            self.election_event.set()
            print(f"Node {self.rank} acknowledged by Leader Node {self.leader_rank}.")
        else:
            # print(f"In else with {data}")
            unique_id, _, _, _ = parse_request(data)
            if unique_id not in self.in_process:
                completed = False
                # print("In start")
                while not completed:
                    try:
                        if self.is_leader and len(self.servers) != 1 and len(self.queue) != 0:
                            server_queue = self.queue.pop(0)
                            self.queue.append(server_queue)
                            # threading.Thread(target=self.client_handler, args=(client, server_queue)).start()
                            # print("Here1")
                            self.client_handler(client, server_queue, data)
                            # self.queue.append(server_queue)
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

                if self.is_leader and child_server != 'None':
                    if operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        if self.semaphores.get(file_name):
                            self.semaphores.update({file_name: False})
                        else:
                            raise Exception(f"Semaphore for file {file_name} is taken")
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
                            print(f"Error in leader sending to child: {e}")
                            pass
                        if not response:
                            print(f"No response, Retry {retry_count + 1} for server {child_server}")
                            time.sleep(self.retry_delay)
                            retry_count += 1
                    if not response:
                        # TODO check this later
                        #  print(f"After {self.max_retries} retries, leader assumes server {child_server} is dead.")
                        #  self.servers.remove(child_server)
                        #  print(f"New child servers available are {self.servers} is dead.")
                        raise Exception(f"{child_server} server is dead")

                    if operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        _, operation2, file_name, file_data = parse_request(response)

                        if operation2 == "REPLICATE":
                            response = handle_request(response, self.file_manager)
                            print("Starting replication manager")
                            self.replication_manager.replicate(unique_id, file_name, file_data, operation)
                            self.semaphores.update({file_name: True})
                            if "SUCCESSFUL" in response:
                                response = f"Operation {operation} successful"
                        else:
                            response = operation + " operation failed"
                        self.semaphores.update({file_name: True})
                        self.critical.update({unique_id: file_name})
                    # if operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                    self.semaphores.update({file_name: True})
                else:
                    response = handle_request(data, self.file_manager)
                    if not self.is_leader and operation in ["WRITE", "EDIT", "DELETE", "CREATE"]:
                        # socket_replication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        if "successfully" in response:
                            print("here2")
                            x = "'"
                            if operation == "CREATE":
                                response = f"{unique_id} REPLICATE {file_name} {x}"
                            else:
                                response = f"{unique_id} REPLICATE {file_name} {file_data}"
                    if operation in ["WRITE", "EDIT", "DELETE", "CREATE", "REPLICATE"]:
                        self.critical.update({unique_id: file_name})
                    self.semaphores.update({file_name: True})
                self.history.update({unique_id: response})
                try:
                    client_socket.sendall(response.encode())
                except Exception as e:
                    print(f"Error {e} , Issue in sending response to client or server.")

                # self.request_history.append(unique_id)
                # if child_server != 'None':
                #     self.queue.append(child_server)
        except Exception as e:
            print(f"Error in client handler: {e}")
            raise e


if __name__ == '__main__':
    server = FileServer()
    threading.Thread(target=broadcast_presence, args=(server.rank, server.port, server.broadcast_port, server.host),
                     daemon=True).start()
    threading.Thread(target=server.listen_for_broadcasts, daemon=True).start()
    threading.Thread(target=server.wait_for_leader_ack, daemon=True).start()
    # print("here2")
    # server.wait_for_leader_ack()
    server.start()
