# TODO: Main client application interface. write, read, create, edit, delete, view

#from discovery_client import DiscoveryClient
#from file_operations import FileOperations
#from client_utilities import get_file_size

# # Initialize DiscoveryClient and FileOperations instances
# discovery_client = DiscoveryClient("discovery_server_ip", discovery_server_port)
# file_operations = FileOperations("file_server_ip", file_server_port)

#discovery_client = DiscoveryClient("discovery_server_ip", 127.0.0.1)
#file_operations = FileOperations("file_server_ip", 10001)



##########################################################################################
# # Discover file server
# file_server_info = discovery_client.discover_file_server()

# if file_server_info:
#     # Use file server information to perform file operations
#     file_path_to_upload = "example_file.txt"
#     file_operations.upload_file(file_path_to_upload)

#     file_name_to_download = "example_file.txt"
#     file_operations.download_file(file_name_to_download)

#     # Other client functionalities can be added...
#     # Additional file operations locally on the client side
    
#     # SAVE - Save content to a file
#     content_to_save = "This is a sample content to save."
#     file_operations.save_file(content_to_save, "saved_file.txt")

#     # READ - Read content from a file
#     file_operations.read_file("saved_file.txt")

#     # CREATE - Create a new empty file
#     file_operations.create_file("new_empty_file.txt")

#     # EDIT - Edit an existing file
#     file_operations.edit_file("existing_file.txt", "New content to replace existing content.")

#     # DELETE - Delete a file
#     file_operations.delete_file("file_to_delete.txt")

#     # Close the socket when done
#     file_operations.close_socket()

#     # Example of using client utilities
#     file_size = get_file_size(file_path_to_upload)
#     print(f"Size of file: {file_size} bytes")

# # Utility methods for messaging
#     def send_message(self, message):
#         self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
#         print("Message sent to server:", message)

#     def receive_message(self):
#         data, server = self.client_socket.recvfrom(1024)
#         return data.decode()
    

#     from FileOperations import FileOperations  # Assuming FileOperations class is in a separate file

################################################## FUNCTIONS ##################################################

# def upload_file_to_server(file_server_ip, file_server_port, file_path):
#     file_operations = FileOperations("127.0.0.1", 10001)
#     file_operations.upload_file(file_path)
#     file_operations.close_socket()

# def download_file_from_server(file_server_ip, file_server_port, file_name):
#     file_operations = FileOperations(file_server_ip, file_server_port)
#     file_operations.download_file(file_name)
#     file_operations.close_socket()

# def save_content_locally(content, file_name):
#     file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
#     file_operations.save_file(content, file_name)

# def read_content_locally(file_name):
#     file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
#     file_operations.read_file(file_name)

# def create_empty_file(file_name):
#     file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
#     file_operations.create_file(file_name)

# def edit_existing_file(file_name, new_content):
#     file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
#     file_operations.edit_file(file_name, new_content)

# def delete_file(file_name):
#     file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
#     file_operations.delete_file(file_name)

#########################This code has Upload & Download #############################

# import socket

# class FileClient:
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.client_socket.connect((self.host, self.port))

#     def send_request(self, request):
#         self.client_socket.send(request.encode())
#         response = self.client_socket.recv(1024).decode()
#         print(response)

#     def upload(self, filename):
#         with open(filename, 'rb') as file:
#             self.send_request(f'UPLOAD {filename}')
#             data = file.read(1024)
#             while data:
#                 self.send_request(data.decode())
#                 data = file.read(1024)

#     def download(self, filename):
#         self.send_request(f'DOWNLOAD {filename}')
#         response = self.client_socket.recv(1024).decode()
#         if response != 'File not found':
#             with open(filename, 'wb') as file:
#                 file.write(response.encode())

#     def create(self, filename):
#         self.send_request(f'CREATE {filename}')
    

#     def edit(self, filename, new_content):
#         self.send_request(f'EDIT {filename} {new_content}')

#     def delete(self, filename):
#         self.send_request(f'DELETE {filename}')

#     def close_connection(self):
#         self.send_request('EXIT')
#         self.client_socket.close()

#     def view(self, filename):
#         self.send_request(f'VIEW {filename}')
#         response = self.client_socket.recv(1024).decode()
#         if response != 'File not found':
#             print(f'File content:\n{response}')
#         else:
#             print('File not found')


# if __name__ == "__main__":
#     client = FileClient('127.0.0.1', 12345)
#     while True:
#         command = input('Enter command: ')
#         if command == 'EXIT':
#             client.close_connection()
#             break
#         elif command == 'UPLOAD':
#             filename = input('Enter filename: ')
#             client.upload(filename)
#         elif command == 'DOWNLOAD':
#             filename = input('Enter filename: ')
#             client.download(filename)
#         elif command == 'CREATE':
#             filename = input('Enter filename: ')
#             client.create(filename)
#         elif command == 'EDIT':
#             filename = input('Enter filename: ')
#             new_content = input('Enter new content: ')
#             client.edit(filename, new_content)
#         elif command == 'DELETE':
#             filename = input('Enter filename: ')
#             client.delete(filename)
#         elif command == 'VIEW':
#             filename = input('Enter filename: ')
#             client.view(filename)
#         else:
#             print('Invalid command')

    # Example usage
    #client.upload('example.txt')
    #client.download('example.txt')
    #client.create('new_file.txt')
    #client.edit('new_file.txt', 'New content0000')
    #client.delete('new_file.txt')
    #client.view('new_file.txt')
    #client.close_connection()
            
####################################################################################################

import socket

class FileClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_request(self, request):
        self.client_socket.send(request.encode())
        response = self.client_socket.recv(1024).decode()
        print(response)

    def create(self, filename):
        self.send_request(f'CREATE {filename}')

    def edit(self, filename, new_content):
        self.send_request(f'EDIT {filename} {new_content}')

    def delete(self, filename):
        self.send_request(f'DELETE {filename}')

    def read(self, filename):
        self.send_request(f'READ {filename}')
        response = self.client_socket.recv(1024).decode()
        if response != 'File not found':
            print(f'File content:\n{response}')
        else:
            print(f'File not found: {filename}')

    def write(self, filename, content):
        self.send_request(f'WRITE {filename} {content}')

    def close_connection(self):
        self.send_request('EXIT')
        self.client_socket.close()

if __name__ == "__main__":
    client = FileClient('127.0.0.1', 12345)
    
    while True:
        command = input('Enter command (CREATE, EDIT, DELETE, READ, WRITE, EXIT): ').upper()
        
        if command == 'EXIT':
            client.close_connection()
            break
        elif command == 'CREATE':
            filename = input('Enter filename: ')
            client.create(filename)
        elif command == 'EDIT':
            filename = input('Enter filename: ')
            new_content = input('Enter new content: ')
            client.edit(filename, new_content)
        elif command == 'DELETE':
            filename = input('Enter filename: ')
            client.delete(filename)
        elif command == 'READ':
            filename = input('Enter filename: ')
            client.read(filename)
        elif command == 'WRITE':
            filename = input('Enter filename: ')
            content = input('Enter content: ')
            client.write(filename, content)
        else:
            print('Invalid command')

