#!/usr/bin/env python
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create and configure the Flask application
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run the Flask application in development mode
    app.run(host="0.0.0.0", port=port, debug=True)