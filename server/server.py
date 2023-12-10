# TODO: Main server application interface.
import socket
import threading
import os

class FileServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

    def start(self):
        print(f"Starting server on {self.host}:{self.port}")
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    break
                command, *args = data.decode().split()
                response = self.execute_command(command, args)
                client.sendall(response.encode())
            except Exception as e:
                print(f"Error: {e}")
                break
        client.close()

    def execute_command(self, command, args):
        if command == 'CREATE':
            return self.create_file(*args)
        elif command == 'EDIT':
            return self.edit_file(*args)
        elif command == 'DELETE':
            return self.delete_file(*args)
        elif command == 'UPLOAD':
            return self.upload_file(*args)
        elif command == 'DOWNLOAD':
            return self.download_file(*args)
        else:
            return "Invalid command"

    def create_file(self, file_name):
        if os.path.exists(file_name):
            return f"File {file_name} already exists."
        with open(file_name, 'w') as file:
            file.write('')
        return f"File {file_name} created successfully."

    def edit_file(self, file_name, new_content):
        if not os.path.exists(file_name):
            return f"File {file_name} does not exist."
        with open(file_name, 'w') as file:
            file.write(new_content)
        return f"File {file_name} edited successfully."

    def delete_file(self, file_name):
        if not os.path.exists(file_name):
            return f"File {file_name} does not exist."
        os.remove(file_name)
        return f"File {file_name} deleted successfully."

    def upload_file(self, file_name, file_contents):
        with open(file_name, 'w') as file:
            file.write(file_contents)
        return f"File {file_name} uploaded successfully."

    def download_file(self, file_name):
        if not os.path.exists(file_name):
            return "File not found"
        with open(file_name, 'r') as file:
            return file.read()

if __name__ == "__main__":
    server = FileServer()
    server.start()

