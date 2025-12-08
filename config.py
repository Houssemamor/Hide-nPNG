"""
Configuration constants for the steganography tool.
"""

# Supported image formats
SUPPORTED_FORMATS = {'PNG', 'BMP', 'png', 'bmp'}

# LSB encoding configuration
BITS_PER_CHANNEL = 1  # Use 1 LSB per color channel
CHANNELS_PER_PIXEL = 3  # RGB

# Message format configuration
MESSAGE_LENGTH_SIZE = 4  # Bytes to store message length (supports up to 4GB)
MESSAGE_LENGTH_BITS = MESSAGE_LENGTH_SIZE * 8

# Buffer for capacity calculations
BITS_PER_PIXEL = BITS_PER_CHANNEL * CHANNELS_PER_PIXEL

# Error messages
ERROR_INVALID_FORMAT = "Unsupported image format. Supported: PNG, BMP"
ERROR_IMAGE_TOO_SMALL = "Image is too small to hide the document. Minimum capacity: {min_bytes} bytes"
ERROR_FILE_NOT_FOUND = "File not found: {path}"
ERROR_INVALID_MESSAGE = "Failed to decode message from image"
