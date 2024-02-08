import socket
import struct
import threading
import time
# from broadcast_handler import BroadCastHandler


class ElectionHandler:
    def __init__(self, node):
        self.node = node
        # self.all_nodes_info = all_nodes_info

    def start_election(self):
        print(f"Node {self.node.rank} is starting an election.")
        self.node.leader = None
        self.node.is_leader = False
        # print(f"In start election , keys are: {self.node.servers.keys()}")
        new_dict = []
        for elem in self.node.servers.keys():
            if elem:
                new_dict.append(elem)

        # self.node.servers.pop(None)
        higher_nodes = [n for n in new_dict if n > self.node.rank and self.node.is_active]
        if not higher_nodes:
            self.declare_victory()
            return
        print(f"Higher nodes is: {higher_nodes}")
        for node in higher_nodes:
            print(f"Sending 'ELECTION' to node {node} at {self.node.servers.get(node)[1]}")
            self.node.send_message(self.node.servers.get(node)[0], self.node.servers.get(node)[1], "ELECTION")

        time.sleep(10)  # Wait for responses
        if not self.node.leader:
            self.declare_victory()

    # def declare_victory(self):
    #     print(f"Node {self.node.rank} is declaring victory and becoming the leader.")
    #     self.node.is_leader = True
    #     self.node.leader = self.node.rank
    #     self.node.broadcast_handler.send_broadcast_message(f'VICTORY:{self.node.rank}')
    #     self.node.election_event.set()

    def declare_victory(self):
        print(f"Node {self.node.rank} is declaring victory and becoming the leader.")

        self.node.is_leader = True
        self.node.queue = []
        self.node.leader = (self.node.host, self.node.port)
        self.node.leader_rank = self.node.rank
        # Notify other nodes of victory
        for node in self.node.servers.keys():
            if node != self.node.rank:
                self.node.send_message(self.node.servers.get(node)[0], self.node.servers.get(node)[1], f"VICTORY:{self.node.rank}:{self.node.host}:{self.node.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            count = 0
            while count <= 3:
                message = f'VICTORY:{self.node.rank}:{self.node.host}:{self.node.port}'.encode()
                sock.sendto(message, ('<broadcast>', self.node.broadcast_port))
                count += 1
                time.sleep(0.1)
            print(f"Victor sending broad_cast_message")
            # sock.close()
        self.node.election_event.set()


class Node:
    def _init_(self, rank, port, all_nodes_info, broadcast_group, broadcast_port):
        self.rank = rank
        self.port = port
        self.is_leader = False
        self.all_nodes_info = all_nodes_info
        self.is_active = True
        self.leader = None
        self.broadcast_group = broadcast_group
        self.broadcast_port = broadcast_port
        # self.broadcast_handler = BroadCastHandler(broadcast_group, broadcast_port)

        self.election_handler = ElectionHandler(self, all_nodes_info)
        self.election_event = threading.Event()

    def stop_server(self):
        self.running = False
        self.is_active = False

    def wait_for_leader_ack(self, timeout=10):
        print(f"new node waiting for leader ack")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.leader is not None:
                print(f"Node {self.rank}: Acknowledged by leader Node {self.leader}.")
                return
            time.sleep(1)

        # No leader response within timeout
        print(f"Node {self.rank}: No response from leader. Checking for higher-ranked nodes.")
        if not any(n['rank'] > self.rank for n in self.all_nodes_info):
            print(f"new node declaring victory")
            # self.election_handler.declare_victory()
            self.is_leader = True
            self.queue = []
            self.leader = self.rank
            # Notify other nodes of victory
            self.broadcast_handler.send_broadcast_message(f'VICTORY:{self.rank}')
            self.election_event.set()
            # b.c he is leader
        else:
            self.election_handler.start_election()

    def listen_for_broadcasts(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_socket.bind(('', self.broadcast_port))
        while self.is_active:
            try:
                message, _ = broadcast_socket.recvfrom(1024)
                print(f"Node {self.rank} received broadcast message: {message}")
                self.handle_broadcast_message(message.decode())
            except Exception as e:
                print(f"Node {self.rank} error receiving broadcast message: {e}")

    def handle_broadcast_message(self, message):
        print("handling new broadcast message")
        data = message.split(':')
        if data[0] == 'NEW_NODE' and self.is_leader:
            new_node_rank = int(data[1])
            new_node_port = int(data[2])
            new_node_info = {'rank': new_node_rank, 'port': new_node_port}
            if new_node_info not in self.all_nodes_info:
                self.all_nodes_info.append(new_node_info)
                print(f"Leader Node {self.rank} acknowledging new Node {new_node_rank}.")
                self.send_message(new_node_port, f'ACK_LEADER:{self.rank}')

    def run_server(self):
        print(f"Node {self.rank} server starting on port {self.port}.")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen()

        while True:
            client_socket, addr = server_socket.accept()
            message = client_socket.recv(1024).decode()
            self.handle_message(message)
            client_socket.close()

    def handle_message(self, message):
        print(f"Node {self.rank} received message: {message}")
        if message.startswith('ELECTION'):
            threading.Thread(target=self.election_handler.start_election).start()
        elif message.startswith('VICTORY'):
            self.leader = int(message.split(':')[1])
            self.election_event.set()
        elif message.startswith('ACK_LEADER'):
            leader_rank = int(message.split(':')[1])
            self.leader = leader_rank
            print(f"Node {self.rank} acknowledged by Leader Node {leader_rank}.")

    def send_message(self, port, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(('localhost', port))
            client_socket.send(message.encode())
        except ConnectionRefusedError:
            pass
        finally:
            client_socket.close()


import argparse


def main(rank, port, nodes_info, broadcast_group, broadcast_port):
    # Node creation and starting server and broadcast listening threads
    node = Node(rank, port, nodes_info, broadcast_group, broadcast_port)
    # threading.Thread(target=node.run_server, daemon=True).start()
    threading.Thread(target=node.listen_for_broadcasts, daemon=True).start()
    node.wait_for_leader_ack()
    print("Server is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)  # Sleep for some time (e.g., 1 second)
    except KeyboardInterrupt:
        print("Server is shutting down.")

    # The rest of your main function logic


def broadcast_presence(rank, port, broadcast_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f'NEW_NODE:{rank}:{port}'.encode()
        sock.sendto(message, ('<broadcast>', broadcast_port))
        print(f"new node sending broad_cast_message")
        sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distributed System Node")
    parser.add_argument("rank", type=int, help="Rank of the node")
    parser.add_argument("port", type=int, help="Port for the node to listen on")
    args = parser.parse_args()
    nodes_info = []
    broadcast_port = 5005  # Choose an appropriate port for broadcasting
    threading.Thread(target=broadcast_presence, args=(args.rank, args.port, broadcast_port), daemon=True).start()
    broadcast_group = '224.0.0.1'

    main(args.rank, args.port, nodes_info, broadcast_group, broadcast_port)