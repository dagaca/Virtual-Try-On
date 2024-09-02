"""
This module runs the Flask application.
"""
# Import the 'app' variable from the app module
from app import app

# Check if this script is executed as the main program
if __name__ == '__main__':
    # Run the Flask application in debug mode and make it accessible externally
    app.run(debug=True, host="0.0.0.0")
