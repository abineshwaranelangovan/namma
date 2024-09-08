from flask import Flask, render_template, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import os
import uuid

app = Flask(__name__)

# Directory for storing generated images
GENERATED_IMAGES_DIR = 'static/generated_images'

# Ensure the directory exists
if not os.path.exists(GENERATED_IMAGES_DIR):
    os.makedirs(GENERATED_IMAGES_DIR)

@app.route('/')
def index():
    return render_template('index.html')  # Ensure this file is in the templates folder

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    user_image = request.files['file']
    if user_image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Target background dimensions
        target_width = 1822
        target_height = 998

        # Open the user-uploaded image
        user_image = Image.open(user_image)

        # Remove background
        user_image_no_bg = remove(user_image)

        # Open the predefined background
        background = Image.open('static/background.jpg').resize((target_width, target_height))

        # Get dimensions of the user image
        user_width, user_height = user_image_no_bg.size

        # Calculate the scaling factor to fit the image within the target width or height
        scale_factor = min(target_width / user_width, target_height / user_height)

        # Decrease the size a little bit by reducing the scale factor
        scale_factor *= 0.7  # Decrease the image size by 30%

        # Resize the user image based on the adjusted scale factor
        new_width = int(user_width * scale_factor)
        new_height = int(user_height * scale_factor)
        user_image_no_bg = user_image_no_bg.resize((new_width, new_height))

        # Calculate x and y positions to center the image and place it at the bottom
        x_position = (target_width - new_width) // 2  # Center horizontally

        # Move the image slightly to the left (adjust the value as needed)
        x_offset = 130  # Move the image 130 pixels to the left
        x_position = max(x_position - x_offset, 0)  # Ensure it doesn't go out of bounds

        y_position = target_height - new_height  # Align bottom

        # Paste the user image onto the background at the calculated position
        background.paste(user_image_no_bg, (x_position, y_position), user_image_no_bg)

        # Save the image to a file
        file_name = f'{uuid.uuid4().hex}.jpg'  # Generate a unique file name
        file_path = os.path.join(GENERATED_IMAGES_DIR, file_name)
        background.save(file_path, 'JPEG')

        # Send the file to the user
        return send_file(file_path, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
