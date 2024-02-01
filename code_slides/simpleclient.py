import socket
import uuid

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
# server_address = '100.71.11.83'
server_address = '127.0.0.1'
server_port = 10005
# server_address = 'localhost'
# server_port = 8080

# Buffer size
buffer_size = 1024

client_socket.connect((server_address, server_port))

message = 'Hi Server 45!'

try:
    # Send data
    file_name = "testfile.txt"
    unique_id = str(uuid.uuid4())
    command = f"{unique_id} CREATE {file_name} {message}"
    # client_socket.sendto(message.encode(), (server_address, server_port))
    client_socket.sendall(command.encode())
    print('Sent to server: ', command)


    # Receive response
    print('Waiting for response...')
    data, server = client_socket.recvfrom(buffer_size)
    print('Received message from server: ', data.decode())

finally:
    client_socket.close()
    print('Socket closed')
