"""
Flask web application for the steganography tool.
Provides a graphical interface for hiding and extracting documents from images.
"""

from flask import Flask, render_template, request, send_file, jsonify, after_this_request
import os
import tempfile
from werkzeug.utils import secure_filename

from image_handler import load_image, save_image, get_image_capacity_bytes
from steganography import encode_message, decode_message

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'bmp', 'PNG', 'BMP'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename, allowed_exts):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/check-capacity', methods=['POST'])
def check_capacity():
    """Check image capacity for a hidden message."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Invalid image format. Use PNG or BMP.'}), 400
        
        # Save temporarily using a unique file name to avoid Windows file locks
        suffix = os.path.splitext(file.filename)[1]
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, dir=app.config['UPLOAD_FOLDER'], suffix=suffix) as temp_file:
                temp_path = temp_file.name
            file.save(temp_path)

            # Load image and get capacity
            image = load_image(temp_path)
            capacity = get_image_capacity_bytes(image)
            width, height = image.size

            # Explicitly close the in-memory image copy
            image.close()

            return jsonify({
                'capacity': capacity,
                'width': width,
                'height': height,
                'total_pixels': width * height
            }), 200
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except PermissionError:
                    # If Windows still holds the file briefly, it will be cleaned up later
                    pass
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hide', methods=['POST'])
def hide():
    """Hide a document in an image."""
    try:
        if 'image' not in request.files or 'document' not in request.files:
            return jsonify({'error': 'Missing image or document'}), 400
        
        image_file = request.files['image']
        doc_file = request.files['document']
        
        if image_file.filename == '' or doc_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(image_file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Invalid image format. Use PNG or BMP.'}), 400
        
        image_path = None
        doc_path = None
        output_path = None

        try:
            # Save files temporarily using unique names to avoid conflicts
            image_suffix = os.path.splitext(image_file.filename)[1]
            doc_suffix = os.path.splitext(doc_file.filename)[1]

            with tempfile.NamedTemporaryFile(delete=False, dir=app.config['UPLOAD_FOLDER'], suffix=image_suffix) as temp_image:
                image_path = temp_image.name
            with tempfile.NamedTemporaryFile(delete=False, dir=app.config['UPLOAD_FOLDER'], suffix=doc_suffix) as temp_doc:
                doc_path = temp_doc.name

            image_file.save(image_path)
            doc_file.save(doc_path)

            # Load image and document
            image = load_image(image_path)
            with open(doc_path, 'rb') as f:
                message = f.read()

            # Extract file extension for restoration on extraction
            doc_extension = os.path.splitext(doc_file.filename)[1].lstrip('.')

            # Encode message with extension
            modified_image = encode_message(message, image, file_extension=doc_extension if doc_extension else None)

            # Save output
            output_filename = os.path.splitext(image_file.filename)[0] + '_hidden' + \
                             os.path.splitext(image_file.filename)[1]
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(output_filename))
            save_image(modified_image, output_path)
            modified_image.close()

            @after_this_request
            def remove_output_file(response):
                if output_path and os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except PermissionError:
                        pass
                return response

            # Return the modified image
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        finally:
            # Clean up temporary files
            for path in (image_path, doc_path):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except PermissionError:
                        pass
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract', methods=['POST'])
def extract():
    """Extract a hidden document from an image."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Invalid image format. Use PNG or BMP.'}), 400
        
        # Save temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(temp_path)
        
        # Load image and decode
        image = load_image(temp_path)
        message, file_extension = decode_message(image)
        
        # Generate output filename with restored extension
        if file_extension:
            output_filename = 'extracted_document.' + file_extension
        else:
            output_filename = 'extracted_document'
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        with open(output_path, 'wb') as f:
            f.write(message)
        
        # Clean up input file
        os.remove(temp_path)
        
        # Return the extracted document
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except ValueError as e:
        return jsonify({'error': 'Failed to extract: ' + str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum: 50MB'}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
