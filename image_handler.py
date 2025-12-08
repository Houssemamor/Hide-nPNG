"""
Image handler module for loading, saving, and manipulating PNG/BMP images.
Uses Pillow for image I/O and pixel access.
"""

from PIL import Image
import os
from config import SUPPORTED_FORMATS, ERROR_INVALID_FORMAT, ERROR_FILE_NOT_FOUND


def load_image(image_path):
    """
    Load an image from disk.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        PIL.Image.Image: Loaded image in RGB mode.
        
    Raises:
        FileNotFoundError: If image file doesn't exist.
        ValueError: If image format is not supported.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(ERROR_FILE_NOT_FOUND.format(path=image_path))
    
    # Get file extension
    _, ext = os.path.splitext(image_path)
    ext = ext.lstrip('.').upper()
    
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(ERROR_INVALID_FORMAT)
    
    # Load image and convert to RGB
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    return image


def save_image(image, output_path):
    """
    Save an image to disk.
    
    Args:
        image (PIL.Image.Image): Image to save.
        output_path (str): Output file path.
        
    Raises:
        ValueError: If output format is not supported.
    """
    _, ext = os.path.splitext(output_path)
    ext = ext.lstrip('.').upper()
    
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(ERROR_INVALID_FORMAT)
    
    # Save image (PNG/BMP preserves quality without compression loss)
    image.save(output_path, format=ext)


def get_pixel_data(image):
    """
    Extract pixel data from image.
    
    Args:
        image (PIL.Image.Image): Image in RGB mode.
        
    Returns:
        list: Flat list of all pixel values (R, G, B, R, G, B, ...).
    """
    pixels = list(image.getdata())
    # Flatten RGB tuples into single list
    flat_pixels = []
    for pixel in pixels:
        flat_pixels.extend(pixel)
    return flat_pixels


def set_pixel_data(image, pixel_data):
    """
    Set pixel data in an image.
    
    Args:
        image (PIL.Image.Image): Image to modify (in RGB mode).
        pixel_data (list): Flat list of pixel values.
        
    Returns:
        PIL.Image.Image: Modified image.
    """
    # Convert flat list back to RGB tuples
    pixels = []
    for i in range(0, len(pixel_data), 3):
        pixels.append((pixel_data[i], pixel_data[i+1], pixel_data[i+2]))
    
    image.putdata(pixels)
    return image


def get_image_capacity_bytes(image):
    """
    Calculate maximum bytes that can be hidden in image (accounting for length header).
    
    Args:
        image (PIL.Image.Image): Image to check.
        
    Returns:
        int: Maximum bytes that can be hidden (excluding length header).
    """
    width, height = image.size
    total_pixels = width * height
    total_bits = total_pixels * 3  # 3 bits per pixel (1 LSB per channel)
    
    # Subtract bits needed for length header
    from config import MESSAGE_LENGTH_BITS
    available_bits = total_bits - MESSAGE_LENGTH_BITS
    available_bytes = available_bits // 8
    
    return available_bytes
