import json
import os
import google.generativeai as genai
from flask import Flask, jsonify, request, send_file, send_from_directory

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'AIzaSyCjFPW-i1rRx7d_po2VZxUElDaBaEancno'

genai.configure(api_key=API_KEY)

app = Flask(__name__)


@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if API_KEY == 'TODO':
            return jsonify({ "error": '''
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
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))

def generate_image_with_imagen(prompt, api_key):
    """
    Generates an image using the Imagen API.

    Args:
        prompt: The text prompt to generate an image from.
        api_key: Your Imagen API key.

    Returns:
        A dictionary containing the generated image data or an error message.
    """

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel('imagen') 
        response = model.generate_content(
            [
                genai.Input(text=prompt)
            ]
        )

        # Assuming the response contains a single image
        image_data = response.candidates[0].artifacts[0].base64

        return {"image_data": image_data}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

# Example usage:
result = generate_image_with_imagen("A cute cat wearing a hat", "YOUR_API_KEY")
if "error" in result:
    print(result["error"])
else:
    # Process the image data (e.g., save it to a file)
    print("Image generated successfully!")
    # ...
