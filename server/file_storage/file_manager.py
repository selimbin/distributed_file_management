# server/file_storage/file_manager.py

import os

class FileManager:
    def __init__(self, server_name, storage_path='file_storage/storage'):
        self.storage_path = storage_path + '/' + server_name
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def save_file(self, file_name, data):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        with open(path, 'wb') as file:
            file.write(data)
        return "File saved successfully."

    def read_file(self, file_name):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        with open(path, 'rb') as file:
            return str(file.read())

    def create_file(self, file_name):
        path = os.path.join(self.storage_path, file_name)
        if os.path.exists(path):
            return "File already exists."
        with open(path, 'w') as file:
            file.write('')
        return "File created successfully."

    def edit_file(self, file_name, new_content):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        with open(path, 'w') as file:
            file.write(new_content)
        return "File edited successfully."

    def delete_file(self, file_name):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        os.remove(path)
        return "File deleted successfully."

    def replicate(self, file_name, data):
        path = os.path.join(self.storage_path, file_name)
        with open(path, 'wb') as file:
            file.write(data)
        return "REPLICATION SUCCESSFUL"

    # Add more file management methods as needed
