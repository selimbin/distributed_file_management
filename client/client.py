# TODO: Main client application interface.

from discovery_client import DiscoveryClient
from file_operations import FileOperations
from client_utilities import get_file_size

# Initialize DiscoveryClient and FileOperations instances
discovery_client = DiscoveryClient("discovery_server_ip", discovery_server_port)
file_operations = FileOperations("file_server_ip", file_server_port)

# Discover file server
file_server_info = discovery_client.discover_file_server()

if file_server_info:
    # Use file server information to perform file operations
    file_path_to_upload = "example_file.txt"
    file_operations.upload_file(file_path_to_upload)

    file_name_to_download = "example_file.txt"
    file_operations.download_file(file_name_to_download)

    # Other client functionalities can be added...
    # Additional file operations locally on the client side
    
    # SAVE - Save content to a file
    content_to_save = "This is a sample content to save."
    file_operations.save_file(content_to_save, "saved_file.txt")

    # READ - Read content from a file
    file_operations.read_file("saved_file.txt")

    # CREATE - Create a new empty file
    file_operations.create_file("new_empty_file.txt")

    # EDIT - Edit an existing file
    file_operations.edit_file("existing_file.txt", "New content to replace existing content.")

    # DELETE - Delete a file
    file_operations.delete_file("file_to_delete.txt")

    # Close the socket when done
    file_operations.close_socket()

    # Example of using client utilities
    file_size = get_file_size(file_path_to_upload)
    print(f"Size of file: {file_size} bytes")

# Utility methods for messaging
    def send_message(self, message):
        self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
        print("Message sent to server:", message)

    def receive_message(self):
        data, server = self.client_socket.recvfrom(1024)
        return data.decode()
    

    from FileOperations import FileOperations  # Assuming FileOperations class is in a separate file

################################################## FUNCTIONS ##################################################
def upload_file_to_server(file_server_ip, file_server_port, file_path):
    file_operations = FileOperations(file_server_ip, file_server_port)
    file_operations.upload_file(file_path)
    file_operations.close_socket()

def download_file_from_server(file_server_ip, file_server_port, file_name):
    file_operations = FileOperations(file_server_ip, file_server_port)
    file_operations.download_file(file_name)
    file_operations.close_socket()

def save_content_locally(content, file_name):
    file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
    file_operations.save_file(content, file_name)

def read_content_locally(file_name):
    file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
    file_operations.read_file(file_name)

def create_empty_file(file_name):
    file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
    file_operations.create_file(file_name)

def edit_existing_file(file_name, new_content):
    file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
    file_operations.edit_file(file_name, new_content)

def delete_file(file_name):
    file_operations = FileOperations(None, None)  # No need for server IP and port for local operations
    file_operations.delete_file(file_name)
