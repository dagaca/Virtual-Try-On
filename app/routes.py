"""
This module contains routes for the Flask application, including
the virtual try-on endpoint.
"""
from flask import request, jsonify, send_file

from app import app
from app.utils import save_uploaded_file, call_virtual_tryon_api, save_result_file

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    summary: Check the health of the API
    description: This endpoint is used to check if the API is up and running.
    responses:
      200:
        description: API is healthy
    """
    return "OK", 200

@app.route('/tryon', methods=['POST'])
def tryon():
    """
    Virtual Try-On API
    ---
    summary: Perform a virtual try-on of a garment on a person's image
    description: |
      This endpoint processes the uploaded person and garment images
      to perform a virtual try-on.
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: person_img
        type: file
        required: true
        description: The person's image for virtual try-on.
      - in: formData
        name: garment_img
        type: file
        required: true
        description: The garment image for virtual try-on.
      - in: formData
        name: seed
        type: number
        required: false
        default: 0
        description: The seed for randomization.
      - in: formData
        name: randomize_seed
        type: boolean
        required: false
        default: true
        description: Whether to randomize the seed.
    responses:
      200:
        description: A successful response containing the try-on result image
        schema:
          type: file
      400:
        description: Invalid input or missing files
      500:
        description: Server error
    """
    app.logger.info("Received try-on request.")

    # Check if necessary files are provided
    if 'person_img' not in request.files or 'garment_img' not in request.files:
        app.logger.error('Missing required files')
        return jsonify({'error': 'Missing required files'}), 400

    person_img = request.files['person_img']
    garment_img = request.files['garment_img']
    seed = request.form.get('seed', 0, type=float)
    randomize_seed = request.form.get('randomize_seed', True, type=lambda x: x.lower() == 'true')

    try:
        # Save the uploaded files temporarily with custom filenames
        person_img_path = save_uploaded_file(
            person_img,
            app.config['TEMP_FOLDER'],
            'person_image'
        )
        garment_img_path = save_uploaded_file(
            garment_img,
            app.config['TEMP_FOLDER'],
            'garment_image'
        )
        app.logger.info(f"Person image saved to {person_img_path}")
        app.logger.info(f"Garment image saved to {garment_img_path}")

        # Call the Gradio API and get the result
        app.logger.info("Calling virtual try-on API.")
        result_data = call_virtual_tryon_api(
            person_img_path,
            garment_img_path,
            seed,
            randomize_seed
        )
        app.logger.info("API call successful.")

        # Save the result to the results directory
        app.logger.info("Saving the result image.")
        output_image_path = save_result_file(result_data)
        app.logger.info(f"Result image saved to {output_image_path}")

        # Return the path to the file to download
        app.logger.info("Sending result file to client.")
        return send_file(output_image_path, as_attachment=True)

    except FileNotFoundError as e:
        app.logger.error(f'FileNotFoundError: {str(e)}')
        return jsonify({'error': f'File not found: {str(e)}'}), 500
    except TypeError as e:
        app.logger.error(f'TypeError: {str(e)}')
        return jsonify({'error': 'Internal server error: Type issue occurred.'}), 500
    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500
