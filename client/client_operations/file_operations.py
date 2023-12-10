# TODO: Handling file operations like upload, download, create, edit, delete, etc. on the file server.
import os
import socket

class FileOperations:
    def __init__(self, file_server_ip, file_server_port):
        self.file_server_ip = file_server_ip
        self.file_server_port = file_server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def upload_file(self, file_path):
        try:
            self.send_message(f"UPLOAD_REQUEST|{file_path}")
            upload_url = f"http://{self.file_server_ip}:{self.file_server_port}/upload"
            message = f"UPLOAD_REQUEST|{os.path.basename(file_path)}"  # Message format for file upload request

            # Send upload request
            self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
            print("Upload request sent to server")

            # Open the file and send its contents in chunks
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    self.client_socket.sendto(chunk, (self.file_server_ip, self.file_server_port))

            # Send upload completion notification
            self.client_socket.sendto(b"UPLOAD_COMPLETE", (self.file_server_ip, self.file_server_port))
            print("File uploaded successfully")

        except socket.error as e:
            print(f"Socket error uploading file: {e}")
        finally:
            self.client_socket.close()
            print('Socket closed')

    def download_file(self, file_name):
        try:
            self.send_message(f"DOWNLOAD_REQUEST|{file_name}")
            download_url = f"http://{self.file_server_ip}:{self.file_server_port}/download/{file_name}"

            # Send download request to the server
            message = f"DOWNLOAD_REQUEST|{file_name}"
            self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
            print(f"Download request sent for file '{file_name}'")

            # Receive file data in chunks and save to a local file
            with open(file_name, 'wb') as file:
                while True:
                    data, server = self.client_socket.recvfrom(1024)
                    if data == b"FILE_NOT_FOUND":
                        print(f"File '{file_name}' not found on the server")
                        break
                    if data == b"DOWNLOAD_COMPLETE":
                        print(f"File '{file_name}' downloaded successfully")
                        break
                    file.write(data)

        except socket.error as e:
            print(f"Socket error downloading file: {e}")
        finally:
            self.client_socket.close()
            print('Socket closed')


    def create_file(self, file_name):
        try:
            self.send_message(f"CREATE_REQUEST|{file_name}")
            create_url = f"http://{self.file_server_ip}:{self.file_server_port}/create"

            # Send file creation request to the server
            message = f"CREATE_REQUEST|{file_name}"
            self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
            print(f"Create request sent for file '{file_name}'")

            # Wait for response from the server
            data, server = self.client_socket.recvfrom(1024)
            if data == b"FILE_CREATED":
                print(f"File '{file_name}' created successfully on the server")
            else:
                print(f"Failed to create file '{file_name}' on the server")

        except socket.error as e:
            print(f"Socket error creating file: {e}")
        finally:
            self.client_socket.close()
            print('Socket closed')

    def edit_file(self, file_name, new_content):
        # Implement logic to edit/update an existing file on the file server with new_content
        try:
            self.send_message(f"EDIT_REQUEST|{file_name}|{new_content}")
            edit_url = f"http://{self.file_server_ip}:{self.file_server_port}/edit"

            # Send file edit request with new content to the server
            message = f"EDIT_REQUEST|{file_name}|{new_content}"
            self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
            print(f"Edit request sent for file '{file_name}'")

            # Wait for response from the server
            data, server = self.client_socket.recvfrom(1024)
            if data == b"FILE_UPDATED":
                print(f"File '{file_name}' updated successfully on the server")
            else:
                print(f"Failed to update file '{file_name}' on the server")

        except socket.error as e:
            print(f"Socket error editing file: {e}")
        finally:
            self.client_socket.close()
            print('Socket closed')

    def delete_file(self, file_name):
        # Implement logic to delete a file from the file server
        try:
            self.send_message(f"DELETE_REQUEST|{file_name}")
            ##client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            delete_url = f"http://{self.file_server_ip}:{self.file_server_port}/delete"

            # Send file delete request to the server
            message = f"DELETE_REQUEST|{file_name}"
            self.client_socket.sendto(str.encode(message), (self.file_server_ip, self.file_server_port))
            print(f"Delete request sent for file '{file_name}'")

            # Wait for response from the server
            data, server = self.client_socket.recvfrom(1024)
            if data == b"FILE_DELETED":
                print(f"File '{file_name}' deleted successfully from the server")
            else:
                print(f"Failed to delete file '{file_name}' from the server")

        except socket.error as e:
            print(f"Socket error deleting file: {e}")
        finally:
            self.client_socket.close()
            print('Socket closed')