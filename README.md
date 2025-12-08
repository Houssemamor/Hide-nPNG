# Hide'nPNG - Steganography Tool

A Python tool to hide and extract secret documents inside digital images (PNG, BMP) without visibly altering the image. Uses LSB (Least Significant Bit) steganography for reliable, lossless encoding.

## Features

- **Hide documents** in PNG/BMP images using LSB encoding
- **Extract documents** from images with faithful reconstruction
- **File extension preservation** - automatically restores original file type (e.g., `.pdf`, `.txt`, `.zip`)
- **Command-line interface** for easy operation
- **Capacity checking** to ensure documents fit in images
- **Flask web app** (optional) for graphical interface
- **Comprehensive tests** for reliability and robustness
- **Error handling** for invalid images, formats, and file sizes

## Installation

### Requirements
- Python 3.7+
- Pillow (image processing)
- NumPy (optional, for optimization)
- Flask (optional, for web interface)

### Setup

1. Clone or download the project:
```bash
cd Hide'nPNG
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface

#### Hide a document in an image

```bash
python main.py hide image.png secret.txt -o output.png
```

**Arguments:**
- `image.png` - The cover image (PNG or BMP)
- `secret.txt` - The document to hide
- `-o output.png` - Output path (optional; defaults to `image_name_hidden.ext`)

**Example:**
```bash
python main.py hide cover.png confidential.pdf -o cover_with_secret.png
# Stores the .pdf extension, will be restored on extraction
```

#### Extract a document from an image

```bash
python main.py extract cover_with_secret.png
```

**Arguments:**
- `cover_with_secret.png` - The image containing a hidden document
- Output path is optional; if omitted, uses auto-generated name with restored extension

**Example:**
```bash
python main.py extract cover_with_secret.png extracted.pdf
# Or auto-generate: python main.py extract cover_with_secret.png
# Output: cover_extracted.pdf (extension automatically restored!)
```

### Checking Image Capacity

To check if your document fits in an image:
```python
from image_handler import load_image, get_image_capacity_bytes

image = load_image('myimage.png')
capacity = get_image_capacity_bytes(image)
print(f"This image can hide up to {capacity} bytes")
```

## File Extension Preservation

A key feature of Hide'nPNG is **automatic file extension preservation**:

- When hiding a document, the original file extension is stored with the hidden data
- When extracting, the extension is automatically restored
- No need to manually specify the output file extension

**Example:**
```bash
# Hide a PDF file
python main.py hide cover.png important.pdf -o cover_hidden.png

# Extract - extension is automatically restored!
python main.py extract cover_hidden.png
# Output: cover_extracted.pdf ✓

# Works with any file type
python main.py hide cover.png archive.zip
python main.py extract cover_hidden.png
# Output: cover_extracted.zip ✓
```

**How it works:**
- Extension is stored as UTF-8 text (max 255 characters)
- Minimal overhead: 1 byte for length + extension size
- Transparent to user - no extra configuration needed

## How It Works

### LSB Steganography

The tool uses **Least Significant Bit (LSB) encoding**:

1. **Message Format:**
   - First 4 bytes: Message length (big-endian 32-bit integer)
   - Remaining bytes: Actual message data

2. **Encoding:**
   - Convert message to binary
   - Replace the least significant bit of each pixel channel (R, G, B) with message bits
   - Visually, the image appears unchanged (LSB changes are imperceptible)

3. **Decoding:**
   - Extract LSBs from pixel channels in order
   - Read first 4 bytes to get message length
   - Extract remaining bits and convert back to bytes

### Capacity Calculation

For an image of size W × H:
- Total pixels: W × H
- Bits per pixel: 3 (one LSB per RGB channel)
- Header size: 32 bits (for message length)
- **Maximum capacity:** `(W × H × 3 - 32) / 8` bytes

Example: A 100×100 image can hide approximately **3,746 bytes** (~3.7 KB)

## Examples

### Hide a Text File
```bash
python main.py hide landscape.png secret_message.txt -o landscape_secret.png
```

### Hide a Binary File
```bash
python main.py hide photo.bmp private_key.bin -o photo_secure.bmp
```

### Extract and Verify
```bash
python main.py extract photo_secure.bmp recovered_key.bin
```

## Testing

Run the comprehensive test suite:
```bash
python test_steganography.py
```

Tests cover:
- Image loading/saving (PNG, BMP)
- Encoding/decoding with various message types
- Large messages and edge cases
- Binary data and special characters
- Full integration workflow

## Supported Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| PNG    | ✓    | ✓     | Recommended; lossless |
| BMP    | ✓    | ✓     | Supported; larger file size |

## API Reference

### Main Functions

#### `image_handler.py`
- `load_image(path)` - Load PNG/BMP image
- `save_image(image, path)` - Save image to file
- `get_pixel_data(image)` - Extract flat pixel array
- `set_pixel_data(image, data)` - Modify pixel data
- `get_image_capacity_bytes(image)` - Calculate max capacity

#### `steganography.py`
- `encode_message(message_bytes, image, file_extension=None)` - Hide message in image with optional extension storage
- `decode_message(image)` - Extract message and file extension from image (returns tuple: (message, extension))

### Configuration

Edit `config.py` to adjust:
- `BITS_PER_CHANNEL` - Bits per color channel (default: 1 for LSB)
- `MESSAGE_LENGTH_SIZE` - Bytes for length header (default: 4)
- `SUPPORTED_FORMATS` - Supported image formats

## Web Interface (Flask)

Optional Flask app for graphical use (if Flask is installed):

```bash
python app.py
```

Then open `http://localhost:5000` in your browser to:
- Upload images
- Hide documents via web form
- Extract documents from images
- View image capacity information

## Security Notes

**Important:** LSB steganography is:
- ✓ **Visually undetectable** in most cases
- ✗ **NOT cryptographically secure** (data is in plaintext in LSBs)
- ✗ **Vulnerable to steganalysis** (statistical analysis can detect hidden data)

**Recommendations:**
- Combine with encryption for true secrecy: Encrypt message → Hide encrypted data
- Use larger images to distribute data (harder to detect)
- Avoid repeated patterns that might reveal presence of data

## Limitations

- **Capacity:** Limited by image size
- **Lossless formats only:** JPEG or other lossy formats will destroy hidden data
- **Format preservation:** Re-saving as lossy format will lose the hidden message
- **No encryption:** Consider encrypting sensitive data before hiding

## Performance

- **Encoding:** ~10-50 MB/s (depends on image size)
- **Decoding:** ~10-50 MB/s
- **Memory:** O(image_width × image_height × 3 bytes)

## Troubleshooting

### "Image too small to hide the document"
- Use a larger cover image (capacity increases with pixel count)
- Try hiding a smaller document

### "Failed to decode message from image"
- Ensure you're extracting from the correct image
- The image might have been modified/recompressed (use PNG/BMP formats only)
- Try re-encoding the message

### "Unsupported image format"
- Convert your image to PNG or BMP first (use an image editor or ImageMagick)
- Supported: PNG, BMP
- Not supported: JPEG, GIF, WEBP, etc.

## Project Structure

```
Hide'nPNG/
├── main.py                  # CLI entry point
├── steganography.py         # Core LSB encoding/decoding
├── image_handler.py         # Image I/O with Pillow
├── config.py                # Configuration constants
├── app.py                   # Flask web interface (optional)
├── test_steganography.py    # Test suite
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Learning Objectives Achieved

- ✓ Study steganography principles and image formats
- ✓ Set up project skeleton and import/read pixels
- ✓ Develop message encoding function
- ✓ Develop message decoding function
- ✓ Perform functional tests and error handling
- ✓ Design CLI interface
- ✓ Create comprehensive documentation

## Future Enhancements

- [ ] Multi-bit LSB encoding (2-4 bits per channel for more capacity)
- [ ] Encryption integration (AES encryption before hiding)
- [ ] Steganalysis resistance techniques
- [ ] Support for RGBA images (4 channels)
- [ ] Batch processing (hide in multiple images)
- [ ] Performance optimizations with NumPy

## License

This project is provided as-is for educational purposes.

## Author

Hide'nPNG Steganography Tool - December 2025
