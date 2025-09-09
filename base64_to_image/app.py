from flask import Flask, render_template, request, jsonify, send_file
import base64
import io
import os
from PIL import Image
import uuid

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_base64_to_image():
    try:
        data = request.get_json()
        base64_data = data.get('base64_data', '')
        
        if not base64_data:
            return jsonify({'error': 'No base64 data provided'}), 400
        
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        # Decode base64 data
        try:
            image_data = base64.b64decode(base64_data)
        except Exception as e:
            return jsonify({'error': f'Invalid base64 data: {str(e)}'}), 400
        
        # Create PIL Image from bytes
        try:
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save image as PNG
        image.save(filepath, 'PNG')
        
        # Return the image URL
        return jsonify({
            'success': True,
            'image_url': f'/image/{filename}',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/image/<filename>')
def serve_image(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/png')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving image: {str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_images():
    try:
        # Clear all uploaded images
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'Error clearing images: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True)
