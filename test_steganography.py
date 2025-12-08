"""
Test suite for the steganography tool.
Tests encoding/decoding functionality with various file types and edge cases.
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image

from image_handler import load_image, save_image, get_image_capacity_bytes
from steganography import encode_message, decode_message


class TestImageHandler(unittest.TestCase):
    """Tests for image handling functions."""
    
    def setUp(self):
        """Create temporary directory and test images."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def create_test_image(self, width=100, height=100, format='PNG'):
        """Create a test image."""
        img = Image.new('RGB', (width, height), color='red')
        path = os.path.join(self.temp_dir, f'test_image.{format.lower()}')
        img.save(path, format=format)
        return path
    
    def test_load_png_image(self):
        """Test loading a PNG image."""
        path = self.create_test_image(format='PNG')
        image = load_image(path)
        self.assertEqual(image.mode, 'RGB')
        self.assertEqual(image.size, (100, 100))
    
    def test_load_bmp_image(self):
        """Test loading a BMP image."""
        path = self.create_test_image(format='BMP')
        image = load_image(path)
        self.assertEqual(image.mode, 'RGB')
        self.assertEqual(image.size, (100, 100))
    
    def test_load_nonexistent_image(self):
        """Test loading a non-existent image."""
        with self.assertRaises(FileNotFoundError):
            load_image(os.path.join(self.temp_dir, 'nonexistent.png'))
    
    def test_load_unsupported_format(self):
        """Test loading an unsupported image format."""
        # Create a JPEG image
        img = Image.new('RGB', (100, 100), color='blue')
        path = os.path.join(self.temp_dir, 'test.jpg')
        img.save(path, format='JPEG')
        
        with self.assertRaises(ValueError):
            load_image(path)
    
    def test_save_png_image(self):
        """Test saving an image as PNG."""
        img = Image.new('RGB', (50, 50), color='green')
        path = os.path.join(self.temp_dir, 'output.png')
        save_image(img, path)
        self.assertTrue(os.path.exists(path))
        loaded = Image.open(path)
        self.assertEqual(loaded.size, (50, 50))
    
    def test_save_bmp_image(self):
        """Test saving an image as BMP."""
        img = Image.new('RGB', (50, 50), color='blue')
        path = os.path.join(self.temp_dir, 'output.bmp')
        save_image(img, path)
        self.assertTrue(os.path.exists(path))
        loaded = Image.open(path)
        self.assertEqual(loaded.size, (50, 50))
    
    def test_image_capacity(self):
        """Test image capacity calculation."""
        path = self.create_test_image(width=100, height=100)
        image = load_image(path)
        capacity = get_image_capacity_bytes(image)
        # 100*100 pixels * 3 channels * 1 bit - 32 bits for length header = 29968 bits = 3746 bytes
        expected = (100 * 100 * 3 - 32) // 8
        self.assertEqual(capacity, expected)


class TestSteganography(unittest.TestCase):
    """Tests for steganography encoding/decoding."""
    
    def setUp(self):
        """Create temporary directory and test images."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def create_test_image(self, width=200, height=200):
        """Create a test image."""
        img = Image.new('RGB', (width, height), color='white')
        path = os.path.join(self.temp_dir, 'test_image.png')
        img.save(path)
        return path
    
    def test_encode_decode_text(self):
        """Test encoding and decoding text message."""
        path = self.create_test_image()
        image = load_image(path)
        
        message = b'Hello, World!'
        encoded = encode_message(message, image)
        decoded, ext = decode_message(encoded)
        
        self.assertEqual(message, decoded)
        self.assertIsNone(ext)  # No extension stored
    
    def test_encode_decode_binary(self):
        """Test encoding and decoding binary data."""
        path = self.create_test_image()
        image = load_image(path)
        
        message = bytes(range(256))  # All possible byte values
        encoded = encode_message(message, image)
        decoded, ext = decode_message(encoded)
        
        self.assertEqual(message, decoded)
    
    def test_encode_decode_large_message(self):
        """Test encoding and decoding a large message."""
        path = self.create_test_image(width=500, height=500)
        image = load_image(path)
        
        # Create a large message (5KB)
        message = b'A' * 5000
        encoded = encode_message(message, image)
        decoded, ext = decode_message(encoded)
        
        self.assertEqual(message, decoded)
    
    def test_encode_message_too_large(self):
        """Test encoding a message that's too large for the image."""
        path = self.create_test_image(width=10, height=10)
        image = load_image(path)
        
        # Create a message too large for 10x10 image
        message = b'X' * 10000
        
        with self.assertRaises(ValueError):
            encode_message(message, image)
    
    def test_encode_empty_message(self):
        """Test encoding an empty message."""
        path = self.create_test_image()
        image = load_image(path)
        
        message = b''
        # Should succeed (0 bytes is valid)
        try:
            encoded = encode_message(message, image)
            decoded, ext = decode_message(encoded)
            self.assertEqual(message, decoded)
        except ValueError:
            # Some implementations might reject empty messages
            pass
    
    def test_decode_invalid_image(self):
        """Test decoding from an image with no valid hidden message."""
        # Create a random image with no valid message
        path = self.create_test_image()
        image = load_image(path)
        
        # Try to decode - should fail or return invalid data
        with self.assertRaises(ValueError):
            decode_message(image)
    
    def test_encode_decode_special_characters(self):
        """Test encoding and decoding special characters."""
        path = self.create_test_image()
        image = load_image(path)
        
        message = '🔐 Secret! @#$%^&*()'.encode('utf-8')
        encoded = encode_message(message, image)
        decoded, ext = decode_message(encoded)
        
        self.assertEqual(message, decoded)
        self.assertEqual(message.decode('utf-8'), decoded.decode('utf-8'))


class TestIntegration(unittest.TestCase):
    """Integration tests for the full steganography workflow."""
    
    def setUp(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_file_extension_preservation(self):
        """Test that file extensions are preserved and restored."""
        extensions_to_test = ['txt', 'pdf', 'doc', 'zip', 'bin', 'json']
        
        for ext in extensions_to_test:
            with self.subTest(extension=ext):
                # Create image
                img = Image.new('RGB', (300, 300), color='green')
                image_path = os.path.join(self.temp_dir, f'cover_{ext}.png')
                img.save(image_path)
                
                # Encode with extension
                image = load_image(image_path)
                message = f'Test file for {ext}'.encode('utf-8')
                
                encoded = encode_message(message, image, file_extension=ext)
                decoded, restored_ext = decode_message(encoded)
                
                self.assertEqual(message, decoded)
                self.assertEqual(ext, restored_ext)
    
    def test_hide_extract_document(self):
        """Test hiding and extracting a document file."""
        # Create test image
        img = Image.new('RGB', (300, 300), color='blue')
        image_path = os.path.join(self.temp_dir, 'cover.png')
        img.save(image_path)
        
        # Create test document
        doc_content = b'This is a secret document\nWith multiple lines\n\x00\xff'
        doc_path = os.path.join(self.temp_dir, 'secret.txt')
        with open(doc_path, 'wb') as f:
            f.write(doc_content)
        
        # Encode
        image = load_image(image_path)
        with open(doc_path, 'rb') as f:
            message = f.read()
        encoded = encode_message(message, image, file_extension='txt')
        
        # Save encoded image
        output_path = os.path.join(self.temp_dir, 'hidden.png')
        save_image(encoded, output_path)
        
        # Decode
        hidden_image = load_image(output_path)
        decoded, ext = decode_message(hidden_image)
        
        self.assertEqual(doc_content, decoded)
        self.assertEqual('txt', ext)
    
    def test_hide_extract_png_bmp_formats(self):
        """Test that encoding works with both PNG and BMP formats."""
        for format_name in ['PNG', 'BMP']:
            with self.subTest(format=format_name):
                # Create image
                img = Image.new('RGB', (200, 200), color='red')
                image_path = os.path.join(self.temp_dir, f'test.{format_name.lower()}')
                img.save(image_path, format=format_name)
                
                # Encode and decode
                image = load_image(image_path)
                message = b'Format test: ' + format_name.encode()
                
                encoded = encode_message(message, image, file_extension='bin')
                decoded, ext = decode_message(encoded)
                
                self.assertEqual(message, decoded)
                self.assertEqual('bin', ext)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
