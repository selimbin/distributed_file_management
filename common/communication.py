# common/communication.py

# Common communication utilities for the file management system

def encode_message(message):
    """Encode a message for transmission."""
    return message.encode()

def decode_message(message):
    """Decode a received message."""
    return message.decode()