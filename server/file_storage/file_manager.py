# server/file_storage/file_manager.py

import os

class FileManager:
    def __init__(self, server_name, storage_path='file_storage/storage'):
        self.storage_path = storage_path + '/' + server_name
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def all_files(self):
        for file_path in os.listdir(self.storage_path):
            path = os.path.join(self.storage_path, file_path)
            with open(path, 'r') as file:
                yield file_path, str(file.read())

    def save_file(self, file_name, data):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        with open(path, 'w') as file:
            file.write(str(data.decode()))
        return "File saved successfully."

    def read_file(self, file_name):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        with open(path, 'r') as file:
            return str(file.read())

    def create_file(self, file_name):
        path = os.path.join(self.storage_path, file_name)
        if os.path.exists(path):
            return "File already exists."
        with open(path, 'w') as file:
            file.write('')
        return "File created successfully."

    def edit_file(self, file_name, new_content):
        # path = os.path.join(self.storage_path, file_name)
        # if not os.path.exists(path):
        #     return "File not found."
        # with open(path, 'w') as file:
        #
        #     file.write(new_content)
        # return "File edited successfully."
        line_number = int(new_content.split("-", 1)[0])
        content = new_content.split("-", 1)[1]
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."

        # Read the file and capture all lines
        with open(path, 'r') as file:
            lines = file.readlines()

        # Check if line_number is valid
        if line_number < 1 or line_number > len(lines):
            return "Line number is out of range."

        # Edit the specific line; line_number is adjusted for 0-based indexing
        lines[line_number - 1] = content + '\n'

        # Write the updated lines back to the file
        with open(path, 'w') as file:
            file.writelines(lines)
        return "File edited successfully."

    def delete_file(self, file_name):
        path = os.path.join(self.storage_path, file_name)
        if not os.path.exists(path):
            return "File not found."
        os.remove(path)
        return "File deleted successfully."

    def replicate(self, file_name, data):
        path = os.path.join(self.storage_path, file_name)
        try:
            data = data.decode()
        except:
            pass
        if data == '!del!':
            if os.path.exists(path):
                os.remove(path)
            # return "File deleted successfully."
        elif data == "'":
            with open(path, 'w') as file:
                file.write('')
        else:
            with open(path, 'w') as file:
                file.write(data)
        return "REPLICATION SUCCESSFUL"

    # Add more file management methods as needed
