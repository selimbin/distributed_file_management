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

    # Example of using client utilities
    file_size = get_file_size(file_path_to_upload)
    print(f"Size of file: {file_size} bytes")

# Other client functionalities can be added...
