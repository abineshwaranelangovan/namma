from flask import Flask, render_template, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        user_image = request.files['file']
        if user_image.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Target background dimensions
        target_width = 1822
        target_height = 998

        # Open the user-uploaded image
        user_image = Image.open(user_image)

        # Remove background
        user_image_no_bg = remove(user_image)

        # Ensure the background image path is correct
        background_path = 'static/background.jpg'
        if not os.path.isfile(background_path):
            return jsonify({"error": "Background image not found"}), 500

        # Open the predefined background
        background = Image.open(background_path).resize((target_width, target_height))

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

        # Save to a BytesIO object
        img_io = io.BytesIO()
        background.save(img_io, 'JPEG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg')

    except Exception as e:
        # Log the error and return a 500 status code with error message
        app.logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
