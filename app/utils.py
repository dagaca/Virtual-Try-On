"""
This module contains utility functions for handling file operations and interacting
with the Gradio Virtual Try-On API. It includes functions to save uploaded images
temporarily, call the API to perform a virtual try-on, and save the resulting image.
"""
import os
import uuid
import tempfile
from app import app
from werkzeug.utils import secure_filename
from gradio_client import handle_file, Client

client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")

def save_uploaded_file(file, temp_dir, custom_name):
    """
    Save an uploaded file to a temporary location with a custom name and return the path.
    
    Args:
        file (werkzeug.datastructures.FileStorage): The uploaded file.
        temp_dir (str): The directory to save the temporary file.
        custom_name (str): The custom name prefix for the temporary file.

    Returns:
        str: The path to the saved temporary file.
    """
    # Ensure temp directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Use tempfile to create a temporary file with a custom name
    temp_file_path = os.path.join(temp_dir, f"{custom_name}_{uuid.uuid4().hex}.tmp")
    with tempfile.NamedTemporaryFile(
            delete=False,
            dir=temp_dir,
            prefix=f"{custom_name}_",
            suffix=".tmp"
        ) as temp_file:
        file.save(temp_file)
        temp_file_path = temp_file.name

    app.logger.info(f"Saved uploaded file to: {temp_file_path}")
    return temp_file_path

def call_virtual_tryon_api(person_img_path, garment_img_path, seed, randomize_seed):
    """
    Call the Gradio Virtual Try-On API with the provided images and parameters.
    
    Args:
        person_img_path (str): Path to the person's image file.
        garment_img_path (str): Path to the garment's image file.
        seed (float): The seed value for randomization.
        randomize_seed (bool): Whether to randomize the seed.

    Returns:
        bytes: The binary content of the result image.
    """
    app.logger.info(
        "Calling Gradio API with person_img_path: %s, garment_img_path: %s",
        person_img_path,
        garment_img_path
    )
    result = client.predict(
        person_img=handle_file(person_img_path),
        garment_img=handle_file(garment_img_path),
        seed=seed,
        randomize_seed=randomize_seed,
        api_name="/tryon"
    )

    app.logger.info(f"API returned result of type: {type(result[0])}")
    if isinstance(result[0], str):
        app.logger.info(f"API returned a file path: {result[0]}")
        with open(result[0], 'rb') as result_file:
            result_data = result_file.read()
    elif isinstance(result[0], bytes):
        app.logger.info("API returned binary data directly.")
        result_data = result[0]
    else:
        app.logger.error(f"Unexpected result type returned by the API: {type(result[0])}")
        raise TypeError("Unexpected result type returned by the API")

    return result_data

def save_result_file(result_data):
    """
    Save the result data to the results directory using a unique GUID.

    Args:
        result_data (bytes): The binary data to save.

    Returns:
        str: The path to the saved result file.
    """
    unique_filename = f"{uuid.uuid4()}.png"  # Generate a unique filename using a GUID
    output_image_path = os.path.abspath(os.path.join(
        app.config['RESULT_FOLDER'], secure_filename(unique_filename))
    )

    # Ensure the results directory exists
    if not os.path.exists(app.config['RESULT_FOLDER']):
        os.makedirs(app.config['RESULT_FOLDER'])
        app.logger.info(f"Created results directory at {app.config['RESULT_FOLDER']}")

    with open(output_image_path, 'wb') as f:
        f.write(result_data)
    app.logger.info(f"Result saved to: {output_image_path}")
    return output_image_path
