import socket
import asyncio
import socket
import threading
import time
import uuid


class FileClient:
    def __init__(self):
        # self.host = host
        # self.port = port

        # self.host = '172.20.10.5'
        # self.port = 10005
        self.leader_host = None
        self.leader_port = None
        self.broadcast_port = 5005
        # self.broadcast_host = '255.255.224.0'
        self.host = '172.20.10.13'
        self.port = 12346

        # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # # self.client_socket.connect(('172.20.10.5', 10005))
        self.queue = []
        self.max_retries = 3
        self.retry_delay = 0.2

    def test(self):
        print('test')
        while True:
            if len(self.queue) > 0:
                request = self.queue.pop(0)
                self.client_socket.send(request.encode())
                print("Message sent to server:", request)
                response = self.client_socket.recv(1024).decode()
                print(response)

    async def send_request(self, request):
        # self.queue.append(request)
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((self.host, self.port))
        # client_socket.send(request.encode())
        # response = client_socket.recv(1024).decode()
        # client_socket.close()
        # print(response)
        # return response
        retry_count = 0
        response = None
        while retry_count <= self.max_retries and not response:
            print(f"Leader host: {self.leader_host}, Leader port: {self.leader_port}")
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                # client_socket.bind((self.host, self.port))
                client_socket.connect((self.leader_host, self.leader_port))
                client_socket.send(request.encode())
                # response = await client_socket.recv(1024)
                response = await asyncio.to_thread(client_socket.recv, 1024)
                response = response.decode()
                client_socket.close()
            except Exception as e:
                print(f"Error sending request: {e}")
            if not response:
                print(f"No Heartbeat, Retry {retry_count + 1} for leader")
                time.sleep(2)
                retry_count += 1
        print(response)
        return response

    def listen_for_broadcasts(self):
        print("listening for broadcasts")
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        broadcast_socket.bind(('', self.broadcast_port))
        while True:
            try:
                message, _ = broadcast_socket.recvfrom(1024)
                print(f"Node Client received broadcast message: {message}")
                # print(f"decoding broadcast: {message.decode()}")
                # data = message.decode().split(':')
                # print("here:" + data[1])
                print(f"Client received broadcast message: {message}")
                self.handle_broadcast_message(message.decode())
            except Exception as e:
                print(f"Client {self.host}:{self.port} error receiving broadcast message: {e}")

    # def handle_request(self, message):
    #     sock = self.sock
    #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #     sock.bind((self.host, self.port))
    #     sock.listen()
    #     print(f"Server listening on {self.host}:{self.port}")
    #     threading.Thread(target=self.heartbeat).start()
    #     threading.Thread(target=self.test_election).start()
    #     threading.Thread(target=self.test_2).start()
    #     while True:
    #         client, _ = sock.accept()
    #         # if self.is_leader and len(self.servers) > 1:
    #         #     self.hold_queue.append(client)
    #         # else:
    #         threading.Thread(target=self.handle_incoming, args=(client,)).start()
    #             # pass

    #         if len(self.hold_queue) > 0 and len(self.queue) > 0:
    #             threading.Thread(target=self.handle_incoming, args=(client,)).start()
    #             pass

    def handle_broadcast_message(self, message):
        data = message.split(':')
        # print(f"Leader: {self.is_leader}: message is : {data}")
        if data[0] == 'LEADER_AT':
            print("handling new broadcast message")
            new_node_ip = data[1]
            new_node_port = int(data[2])
            self.leader_host = new_node_ip
            self.leader_port = new_node_port

    def broadcast_presence(self):
        print("broadcasting presence")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = f'CLIENT:{self.host}:{self.port}'.encode()
            sock.sendto(message, ('<broadcast>', self.broadcast_port))
            print(f"new node sending broad_cast_message")
            sock.close()

    async def create(self, unique_id, filename):
        request = f' {unique_id} CREATE {filename} EMPTY'
        await self.send_request(request)

    # async def edit(self, unique_id, filename, new_content):
    #     request = f' {unique_id} EDIT {filename} {new_content}'
    #     await self.send_request(request)

    async def edit(self, unique_id, filename, line_number, new_content):
        new_content = f'{line_number}-{new_content}'
        request = f'{unique_id} EDIT {filename} {new_content}'
        await self.send_request(request)

    async def delete(self, unique_id, filename):
        request = f'{unique_id} DELETE {filename} EMPTY'
        await self.send_request(request)

    async def read(self, unique_id, filename):
        request = f'{unique_id} READ {filename} EMPTY'
        # response = await self.send_request(f'READ {filename}')
        await self.send_request(request)
        # response = await self.client_socket.recv(1024).decode()
        # if response != 'File not found':
        #     print(f'File content:\n{response}')
        # else:
        #     print(f'File not found: {filename}')

    async def write(self, unique_id, filename, content):
        request = f'{unique_id} WRITE {filename} {content}'
        await self.send_request(request)

    def close_connection(self):
        self.send_request('EXIT')
        self.client_socket.close()

    async def client_input(self):
        while True:

            # unique_id = input("Enter unique id: ")  # Get the unique ID from the user
            # await client.send_request(f"ID {unique_id}")  # Send the unique ID to the server
            unique_id = str(uuid.uuid4())

            command = input('Enter command (CREATE, EDIT, DELETE, READ, WRITE, EXIT): ').upper()
            if command == 'EXIT':
                client.close_connection()
                break

            elif command == 'CREATE':
                self.broadcast_presence()
                retry_count = 0
                while retry_count <= self.max_retries and not self.leader_host:
                    try:
                        self.broadcast_presence()
                    except Exception as e:
                        pass
                    if not self.leader_host:
                        time.sleep(self.retry_delay)
                        retry_count += 1
                if not self.leader_host:
                    print(f"After {self.max_retries} tries, client cannot find leader server.")
                    return
                print("waiting for leader")
                time.sleep(1)
                filename = input('Enter filename: ')
                # content = input('Enter content: ')
                await client.create(unique_id, filename)
                self.leader_host = None
                self.leader_port = None

            # elif command == 'EDIT':
            #     self.broadcast_presence()
            #     while self.leader_host is None:
            #         i = 0
            #     filename = input('Enter filename: ')
            #     new_content = input('Enter new content: ')
            #     await client.edit(unique_id, filename, new_content)
            #     self.leader_host = None
            #     self.leader_port = None

            elif command == 'EDIT':
                self.broadcast_presence()
                retry_count = 0
                while retry_count <= self.max_retries and not self.leader_host:
                    try:
                        self.broadcast_presence()
                    except Exception as e:
                        pass
                    if not self.leader_host:
                        time.sleep(self.retry_delay)
                        retry_count += 1
                if not self.leader_host:
                    print(f"After {self.max_retries} tries, client cannot find leader server.")
                    return
                filename = input('Enter filename: ')
                line_number = int(input('Enter line number to edit: '))
                new_content = input('Enter new content: ')
                await client.edit(unique_id, filename, line_number, new_content)
                self.leader_host = None
                self.leader_port = None

            elif command == 'DELETE':
                self.broadcast_presence()
                retry_count = 0
                while retry_count <= self.max_retries and not self.leader_host:
                    try:
                        self.broadcast_presence()
                    except Exception as e:
                        pass
                    if not self.leader_host:
                        time.sleep(self.retry_delay)
                        retry_count += 1
                if not self.leader_host:
                    print(f"After {self.max_retries} tries, client cannot find leader server.")
                    return
                filename = input('Enter filename: ')
                await client.delete(unique_id, filename)
                self.leader_host = None
                self.leader_port = None
            elif command == 'READ':
                self.broadcast_presence()
                retry_count = 0
                while retry_count <= self.max_retries and not self.leader_host:
                    try:
                        self.broadcast_presence()
                    except Exception as e:
                        pass
                    if not self.leader_host:
                        time.sleep(self.retry_delay)
                        retry_count += 1
                if not self.leader_host:
                    print(f"After {self.max_retries} tries, client cannot find leader server.")
                    return
                filename = input('Enter filename: ')
                await client.read(unique_id, filename)
                self.leader_host = None
                self.leader_port = None
            elif command == 'WRITE':
                self.broadcast_presence()
                retry_count = 0
                while retry_count <= self.max_retries and not self.leader_host:
                    try:
                        self.broadcast_presence()
                    except Exception as e:
                        pass
                    if not self.leader_host:
                        time.sleep(self.retry_delay)
                        retry_count += 1
                if not self.leader_host:
                    print(f"After {self.max_retries} tries, client cannot find leader server.")
                    return
                filename = input('Enter filename: ')
                content = input('Enter content: ')
                await client.write(unique_id, filename, content)
                self.leader_host = None
                self.leader_port = None
            else:
                print('Invalid command')


if __name__ == "__main__":
    client = FileClient()
    threading.Thread(target=client.listen_for_broadcasts).start()
    # threading.Thread(target=client.handle_incoming).start()
    asyncio.run(client.client_input())