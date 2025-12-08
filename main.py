"""
Command-line interface for the steganography tool.
Supports: hide <image> <document> and extract <image> <output>
"""

import argparse
import sys
import os
from pathlib import Path

from image_handler import load_image, save_image, get_image_capacity_bytes
from steganography import encode_message, decode_message


def hide_command(args):
    """
    Hide a document inside an image.
    
    Args:
        args: Argparse namespace with image_path and document_path.
    """
    try:
        # Load the image
        print(f"Loading image: {args.image_path}")
        image = load_image(args.image_path)
        
        # Check capacity
        capacity = get_image_capacity_bytes(image)
        print(f"Image capacity: {capacity} bytes")
        
        # Read the document to hide
        print(f"Reading document: {args.document_path}")
        if not os.path.exists(args.document_path):
            print(f"Error: File not found: {args.document_path}")
            sys.exit(1)
        
        with open(args.document_path, 'rb') as f:
            document_data = f.read()
        
        print(f"Document size: {len(document_data)} bytes")
        
        # Extract file extension for later restoration
        file_extension = Path(args.document_path).suffix.lstrip('.')
        
        # Check if document fits (accounting for extension metadata)
        extension_overhead = len(file_extension) + 1 if file_extension else 1  # 1 byte for length
        if len(document_data) + extension_overhead > capacity:
            print(f"Error: Document too large for image.")
            print(f"  Document size: {len(document_data)} bytes")
            print(f"  Extension metadata: {extension_overhead} bytes")
            print(f"  Total: {len(document_data) + extension_overhead} bytes")
            print(f"  Image capacity: {capacity} bytes")
            sys.exit(1)
        
        # Encode the message with file extension
        print("Encoding message into image...")
        modified_image = encode_message(document_data, image, file_extension=file_extension if file_extension else None)
        
        # Save the modified image
        output_path = args.output_path or Path(args.image_path).stem + "_hidden" + Path(args.image_path).suffix
        print(f"Saving modified image: {output_path}")
        save_image(modified_image, output_path)
        
        print(f"✓ Success! Document hidden in: {output_path}")
        if file_extension:
            print(f"  Original extension (.{file_extension}) will be restored on extraction")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def extract_command(args):
    """
    Extract a hidden document from an image.
    
    Args:
        args: Argparse namespace with image_path and output_path.
    """
    try:
        # Load the image
        print(f"Loading image: {args.image_path}")
        image = load_image(args.image_path)
        
        # Decode the message
        print("Decoding message from image...")
        document_data, file_extension = decode_message(image)
        
        print(f"Extracted message size: {len(document_data)} bytes")
        
        # Determine output filename
        output_path = args.output_path
        if not output_path:
            # Auto-generate filename with restored extension if available
            base_name = Path(args.image_path).stem + "_extracted"
            if file_extension:
                output_path = base_name + "." + file_extension
                print(f"Using restored extension: .{file_extension}")
            else:
                output_path = base_name
        
        print(f"Saving extracted document: {output_path}")
        with open(output_path, 'wb') as f:
            f.write(document_data)
        
        print(f"✓ Success! Document extracted to: {output_path}")
        if file_extension:
            print(f"  Original extension (.{file_extension}) has been restored")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Hide and extract secret documents in PNG/BMP images using LSB steganography.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Hide a document:
    python main.py hide image.png secret.txt -o output.png
    
  Extract a document:
    python main.py extract output.png extracted.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Hide command
    hide_parser = subparsers.add_parser('hide', help='Hide a document in an image')
    hide_parser.add_argument('image_path', help='Path to the image file (PNG/BMP)')
    hide_parser.add_argument('document_path', help='Path to the document to hide')
    hide_parser.add_argument('-o', '--output', dest='output_path', default=None,
                            help='Output image path (default: image_name_hidden.ext)')
    hide_parser.set_defaults(func=hide_command)
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract a document from an image')
    extract_parser.add_argument('image_path', help='Path to the image with hidden document')
    extract_parser.add_argument('output_path', help='Output path for extracted document')
    extract_parser.set_defaults(func=extract_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == '__main__':
    main()
