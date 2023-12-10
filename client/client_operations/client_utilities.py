# TODO: Additional utilities for client processing.
#SAVE, READ, CREATE, EDIT, DELETE

import socket
import os

class FileOperations:
    def __init__(self, file_server_ip, file_server_port):
        self.file_server_ip = file_server_ip
        self.file_server_port = file_server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    # File processing methods
    def save_file(self, file_content, file_name):
        try:
            with open(file_name, 'w') as file:
                file.write(file_content)
            print(f"File '{file_name}' saved locally")
        except IOError as e:
            print(f"Error saving file '{file_name}': {e}")

    def read_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                file_content = file.read()
            print(f"Content of '{file_name}':\n{file_content}")
            return file_content
        except FileNotFoundError:
            print(f"File '{file_name}' not found")
            return None
        except IOError as e:
            print(f"Error reading file '{file_name}': {e}")
            return None

    def create_file(self, file_name):
        try:
            with open(file_name, 'w') as file:
                pass  # Creating an empty file
            print(f"File '{file_name}' created locally")
        except IOError as e:
            print(f"Error creating file '{file_name}': {e}")

    def edit_file(self, file_name, new_content):
        try:
            with open(file_name, 'w') as file:
                file.write(new_content)
            print(f"File '{file_name}' edited locally")
        except IOError as e:
            print(f"Error editing file '{file_name}': {e}")

    def delete_file(self, file_name):
        try:
            os.remove(file_name)
            print(f"File '{file_name}' deleted locally")
        except FileNotFoundError:
            print(f"File '{file_name}' not found")
        except PermissionError as e:
            print(f"Permission error deleting file '{file_name}': {e}")

    def close_socket(self):
        self.client_socket.close()
        print('Socket closed')
