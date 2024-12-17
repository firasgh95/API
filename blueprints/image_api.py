from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
import connection.database as db
import numpy as np
import matplotlib.pyplot as plt
import cv2
import io
from flask import send_file
# Initialize Blueprint
image_api = Blueprint('image_api', __name__)

# Database configuration
DATABASE_NAME = db.database_name
TABLE_NAME = db.table_name
engine = db.engine


def apply_colormap_with_opencv(frame, colormap=cv2.COLORMAP_JET):
    """
    Apply an OpenCV colormap to a 1D grayscale frame.
    Args:
        frame (numpy.array): The pixel values as a 1D numpy array.
        colormap (int): OpenCV colormap constant (e.g., cv2.COLORMAP_JET).
    Returns:
        BytesIO: A buffer containing the colorized image as PNG.
    """
    # Normalize pixel values to 0-255
    normalized_frame = np.interp(
        frame, (frame.min(), frame.max()), (0, 255)).astype(np.uint8)

    # Reshape to a 2D image (Height=1, Width=150)
    image_2d = normalized_frame.reshape((1, -1))

    # Apply the chosen colormap using OpenCV
    colored_image = cv2.applyColorMap(image_2d, colormap)

    # Encode the image as PNG and save it into a buffer
    _, buffer = cv2.imencode('.png', colored_image)
    image_buffer = io.BytesIO(buffer)  # Convert to BytesIO for Flask
    return image_buffer


@image_api.route('/get_colored_frames', methods=['GET'])
def get_colored_frames():
    """
    API endpoint to fetch image frames between depth_min and depth_max
    and apply a colormap using OpenCV.
    """
    try:
        # Parse query parameters
        depth = float(request.args.get('depth'))

        colormap_name = request.args.get(
            'colormap', 'JET')  # Default to JET colormap
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing depth parameters."}), 400

    try:
        # OpenCV Colormap Mapping
        colormap_dict = {
            'JET': cv2.COLORMAP_JET,
            'HOT': cv2.COLORMAP_HOT,
            'COOL': cv2.COLORMAP_COOL,
            'VIRIDIS': cv2.COLORMAP_VIRIDIS,
            'PLASMA': cv2.COLORMAP_PLASMA,
            'INFERNO': cv2.COLORMAP_INFERNO,
            'MAGMA': cv2.COLORMAP_MAGMA,
            'RAINBOW': cv2.COLORMAP_RAINBOW
        }
        colormap = colormap_dict.get(colormap_name.upper(), cv2.COLORMAP_JET)

        # Query the database for the specified depth range
        query = text(
            f"SELECT * FROM {TABLE_NAME} WHERE depth = :depth")
        with engine.connect() as connection:
            result = connection.execute(
                query, {"depth": depth})
            rows = [dict(row) for row in result.mappings()]

        if not rows:
            return jsonify({"message": "No data found for the given depth range."}), 404

        # Process the first frame (you can process all frames if needed)
        # Extract pixel values
        frame_data = np.array([rows[0][f'pixel_{i}'] for i in range(150)])
        colored_image_buffer = apply_colormap_with_opencv(frame_data, colormap)

        # Return the colorized image as a file response
        return send_file(colored_image_buffer, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": f"Failed to process frames: {str(e)}"}), 500


@image_api.route('/get_frames', methods=['GET'])
def get_frames():
    """
    API endpoint to fetch image frames between depth_min and depth_max
    and apply a colormap using OpenCV.
    """
    try:
        # Parse query parameters
        depth_min = float(request.args.get('depth_min'))
        depth_max = float(request.args.get('depth_max'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing depth_min/depth_max parameters."}), 400

    if depth_min > depth_max:
        return jsonify({"error": "depth_min cannot be greater than depth_max."}), 400

    try:

        # Query the database for the specified depth range
        query = text(
            f"SELECT * FROM {TABLE_NAME} WHERE depth BETWEEN :depth_min AND :depth_max")
        with engine.connect() as connection:
            result = connection.execute(
                query, {"depth_min": depth_min, "depth_max": depth_max})
            rows = [dict(row) for row in result.mappings()]

        if not rows:
            return jsonify({"message": "No data found for the given depth range."}), 404
            # Return the colorized image as a file response
        return jsonify({"message": rows}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process frames: {str(e)}"}), 500
