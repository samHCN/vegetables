# vegetables
"""
main.py

This module is the entry point for the application. 
It defines the Flask app and sets up the routes for the application.

The main functionality of this module is to:
- Configure the Gemini API key.
- Define the route for the home page.
- Define the route for handling API requests for content generation.

"""

# Import necessary libraries
import os
from flask import Flask, send_file, request, jsonify
from google.generativeai import genai

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'YOUR_API_KEY' 

genai.configure(api_key=API_KEY)

app = Flask(__name__)


@app.route("/")
def index():
    """
    Route for the home page.
    Returns the index.html file.
    """
    return send_file('web/index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Route for handling API requests for content generation.
    Receives a JSON payload with the content and model information.
    Streams the generated content back to the client.
    """
    if not request.is_json:
        return jsonify({ "error": '''
                    Request body must be JSON.
                    To get started, get an API key at
                    https://g.co/ai/idxGetGeminiKey and enter it in
                    main.py
                    '''.replace('\n', '') })
    try:
        req_body = request.get_json()
        content = req_body.get("contents")
        model = genai.GenerativeModel(model_name=req_body.get("model"))
        response = model.generate_content(content, stream=True)
        def stream():
            for chunk in response:
                yield 'data: %s\n\n' % json.dumps({ "text": chunk.text })

        return stream(), {'Content-Type': 'text/event-stream'}

    except Exception as e:
        return jsonify({ "error": str(e) })


@app.route('/<path:path>')
def catch_all(path):
    """
    Route for handling all other requests.
    Returns a 404 error.
    """
    return jsonify({ "error": "Not found" }), 404


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 9000)))
