"""
Core steganography module for encoding and decoding messages in images.
Uses LSB (Least Significant Bit) encoding for 1-bit per channel.
"""

from config import MESSAGE_LENGTH_SIZE, MESSAGE_LENGTH_BITS, BITS_PER_PIXEL, ERROR_INVALID_MESSAGE


def encode_message(message_bytes, image, file_extension=None):
    """
    Encode a message into an image using LSB steganography.
    
    Args:
        message_bytes (bytes): The message to hide.
        image (PIL.Image.Image): The image to hide the message in.
        file_extension (str): Optional file extension to store with message (e.g., 'txt', 'pdf').
        
    Returns:
        PIL.Image.Image: Modified image with hidden message.
        
    Raises:
        ValueError: If message is too large for the image.
    """
    from image_handler import get_pixel_data, set_pixel_data, get_image_capacity_bytes
    
    # Prepare extension data (1 byte for length + extension string)
    if file_extension:
        # Remove leading dot if present
        file_extension = file_extension.lstrip('.')
        # Limit to 255 chars (1 byte for length)
        file_extension = file_extension[:255]
        extension_bytes = len(file_extension).to_bytes(1, byteorder='big') + file_extension.encode('utf-8')
    else:
        extension_bytes = b'\x00'  # 0 length means no extension
    
    # Combine: extension_data + message_length + message
    message_length = len(message_bytes)
    length_bytes = message_length.to_bytes(MESSAGE_LENGTH_SIZE, byteorder='big')
    full_data = extension_bytes + length_bytes + message_bytes
    
    # Check if full data fits
    max_capacity = get_image_capacity_bytes(image)
    if len(full_data) > max_capacity:
        raise ValueError(
            f"Message too large. Image capacity: {max_capacity} bytes, "
            f"message + metadata size: {len(full_data)} bytes"
        )
    
    # Get pixel data
    pixel_data = get_pixel_data(image)
    
    # Convert all bytes to bits
    bit_string = ''.join(format(byte, '08b') for byte in full_data)
    
    # Pad to ensure we don't overrun
    bit_string = bit_string.ljust(len(pixel_data), '0')
    
    # Embed bits into LSBs
    for i, bit in enumerate(bit_string[:len(pixel_data)]):
        pixel_data[i] = (pixel_data[i] & 0xFE) | int(bit)
    
    # Set modified pixel data back to image
    return set_pixel_data(image, pixel_data)


def decode_message(image):
    """
    Decode and extract a message hidden in an image using LSB steganography.
    
    Args:
        image (PIL.Image.Image): The image to extract the message from.
        
    Returns:
        tuple: (message_bytes, file_extension) where file_extension is str or None
        
    Raises:
        ValueError: If no valid message is found in the image.
    """
    from image_handler import get_pixel_data
    
    # Get pixel data
    pixel_data = get_pixel_data(image)
    
    # Extract bits from LSBs
    bit_string = ''.join(str(pixel & 1) for pixel in pixel_data)
    
    # Extract extension length (first 8 bits)
    extension_length_bits = bit_string[:8]
    try:
        extension_length = int(extension_length_bits, 2)
    except ValueError:
        raise ValueError(ERROR_INVALID_MESSAGE)
    
    # Extract extension if present
    extension_offset = 8
    file_extension = None
    if extension_length > 0:
        extension_bits_needed = extension_length * 8
        extension_bit_string = bit_string[extension_offset:extension_offset + extension_bits_needed]
        
        if len(extension_bit_string) < extension_bits_needed:
            raise ValueError(ERROR_INVALID_MESSAGE)
        
        try:
            extension_bytes = bytes(
                int(extension_bit_string[i:i+8], 2) 
                for i in range(0, len(extension_bit_string), 8)
            )
            file_extension = extension_bytes.decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            raise ValueError(ERROR_INVALID_MESSAGE)
        
        # Move offset past extension
        offset = extension_offset + extension_bits_needed
    else:
        offset = extension_offset
    
    # Extract message length (next MESSAGE_LENGTH_BITS bits)
    length_bit_string = bit_string[offset:offset + MESSAGE_LENGTH_BITS]
    try:
        message_length = int(length_bit_string, 2)
    except ValueError:
        raise ValueError(ERROR_INVALID_MESSAGE)
    
    # Ensure message length is reasonable
    if message_length == 0 or message_length > (len(pixel_data) - offset - MESSAGE_LENGTH_BITS) // 8:
        raise ValueError(ERROR_INVALID_MESSAGE)
    
    # Extract message bits (after length header)
    message_offset = offset + MESSAGE_LENGTH_BITS
    message_bit_string = bit_string[message_offset:]
    message_bits_needed = message_length * 8
    
    if len(message_bit_string) < message_bits_needed:
        raise ValueError(ERROR_INVALID_MESSAGE)
    
    message_bit_string = message_bit_string[:message_bits_needed]
    
    # Convert bits back to bytes
    message_bytes = bytes(
        int(message_bit_string[i:i+8], 2) 
        for i in range(0, len(message_bit_string), 8)
    )
    
    return message_bytes, file_extension
