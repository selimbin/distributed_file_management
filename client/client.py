import socket
import asyncio

class FileClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, 12346))
        self.queue = []

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
        self.client_socket.send(request.encode())
        response = self.client_socket.recv(1024).decode()
        print(response)

    async def create(self, filename):
        await self.send_request(f'CREATE {filename}')

    async def edit(self, filename, new_content):
        await self.send_request(f'EDIT {filename} {new_content}')

    async def delete(self, filename):
        await self.send_request(f'DELETE {filename}')

    async def read(self, filename):
        self.send_request(f'READ {filename}')
        response = self.client_socket.recv(1024).decode()
        if response != 'File not found':
            print(f'File content:\n{response}')
        else:
            print(f'File not found: {filename}')

    async def write(self, filename, content):
        await self.send_request(f'WRITE {filename} {content}')

    def close_connection(self):
        self.send_request('EXIT')
        self.client_socket.close()

    async def client_input(client):
        while True:
            command = input('Enter command (CREATE, EDIT, DELETE, READ, WRITE, EXIT): ').upper()
            
            if command == 'EXIT':
                client.close_connection()
                break
            elif command == 'CREATE':
                filename = input('Enter filename: ')
                await client.create(filename)
            elif command == 'EDIT':
                filename = input('Enter filename: ')
                new_content = input('Enter new content: ')
                await client.edit(filename, new_content)
            elif command == 'DELETE':
                filename = input('Enter filename: ')
                await client.delete(filename)
            elif command == 'READ':
                filename = input('Enter filename: ')
                await client.read(filename)
            elif command == 'WRITE':
                filename = input('Enter filename: ')
                content = input('Enter content: ')
                await client.write(filename, content)
            else:
                print('Invalid command')

if __name__ == "__main__":
    client = FileClient('127.0.0.1', 12345)
    asyncio.run(client.client_input())
