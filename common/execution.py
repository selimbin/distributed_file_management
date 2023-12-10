# common/exceptions.py

# Custom exceptions for the file management system

class FileManagerError(Exception):
    """Base exception class for file manager errors."""
    pass

class FileNotFound(FileManagerError):
    """Exception raised when a file is not found."""
    pass

# Add more custom exceptions as needed
