# server/server_operations/server_utilities.py

def handle_request(request, file_manager):
    # Example request: "SAVE somefile.txt This is the content"
    command, file_name, *content = request.split(maxsplit=2)
    content = content[0] if content else ""

    if command == "SAVE":
        return file_manager.save_file(file_name, content.encode())
    elif command == "READ":
        return file_manager.read_file(file_name).decode()
    elif command == "CREATE":
        return file_manager.create_file(file_name)
    elif command == "EDIT":
        return file_manager.edit_file(file_name, content)
    elif command == "DELETE":
        return file_manager.delete_file(file_name)
    else:
        return "Invalid command"

    # Extend this function to handle more types of requests
