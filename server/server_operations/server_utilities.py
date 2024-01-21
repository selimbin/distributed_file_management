# server/server_operations/server_utilities.py

def handle_request(request, file_manager):
    # Example request: "SAVE somefile.txt This is the content"
    unique_id, command, file_name, *content = request.split(maxsplit=3)
    content = content[0] if content else ""

    if command == "WRITE":
        print(f"In command write: command:{command} | file_name:{file_name}")
        return file_manager.save_file(file_name, content.encode())
    elif command == "READ":
        print(f"In command read: command:{command} | file_name:{file_name}")
        print(f"here: {file_manager.read_file(file_name)}")
        return file_manager.read_file(file_name)
    elif command == "CREATE":
        print(f"In command create: command:{command} | file_name:{file_name}")
        return file_manager.create_file(file_name)
    elif command == "EDIT":
        print(f"In command edit: command:{command} | file_name:{file_name}")
        return file_manager.edit_file(file_name, content)
    elif command == "DELETE":
        print(f"In command delete: command:{command} | file_name:{file_name}")
        return file_manager.delete_file(file_name)
    else:
        print(f"In command invalid: command:{command} | file_name:{file_name}")
        return "Invalid command"

    # Extend this function to handle more types of requests
