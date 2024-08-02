from flask import Flask, request, jsonify, send_file, send_from_directory
import json
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import google.cloud.vision as vision

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = ''

genai.configure(api_key=API_KEY)

app = Flask(__name__)

# Initialize Google Cloud Vision client (replace 'YOUR_PROJECT_ID' with your project ID)
client = vision.ImageAnnotatorClient()

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

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream)

    # Convert image to bytes for Cloud Vision API
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Analyze image with Cloud Vision API
    response = client.annotate_image({
        'image': {'content': img_byte_arr},
        'features': [
            {'type_': vision.Feature.Type.LABEL_DETECTION},
            {'type_': vision.Feature.Type.TEXT_DETECTION},
            # Add more features as needed (e.g., object detection, face detection)
        ]
    })

    # Extract information from response
    labels = [label.description for label in response.label_annotations]
    text = response.full_text_annotation.text

    # Store image (replace with your preferred storage method)
    # image.save('uploads/' + image_file.filename)

    return jsonify({'labels': labels, 'text': text}), 200

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 9000)))
import folium

# Create a map object centered on a location (e.g., London)
m = folium.Map(location=[51.5074, 0.1278], zoom_start=12) 

# Sample farm data (replace with your actual data)
farm_data = {
    "name": "Example Farm",
    "location": [51.4, 0.2],
    "products": "Wheat, Barley"
}

# Create a marker
folium.Marker(
    location=farm_data["location"],
    popup=f"<b>{farm_data['name']}</b><br>Products: {farm_data['products']}",
    tooltip="Click for details"
).add_to(m)

# Save the map to an HTML file
m.save("map.html")
from flask import Flask, request, jsonify, send_file, send_from_directory
import json
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import google.cloud.vision as vision

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'AIzaSyAH17rAIUWAT17_jihVOZXiBUKbcrv2D4w'

genai.configure(api_key=API_KEY)

app = Flask(__name__)

# Initialize Google Cloud Vision client (replace 'YOUR_PROJECT_ID' with your project ID)
client = vision.ImageAnnotatorClient()

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

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream)

    # Convert image to bytes for Cloud Vision API
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Analyze image with Cloud Vision API
    response = client.annotate_image({
        'image': {'content': img_byte_arr},
        'features': [
            {'type_': vision.Feature.Type.LABEL_DETECTION},
            {'type_': vision.Feature.Type.TEXT_DETECTION},
            # Add more features as needed (e.g., object detection, face detection)
        ]
    })

    # Extract information from response
    labels = [label.description for label in response.label_annotations]
    text = response.full_text_annotation.text

    # Store image (replace with your preferred storage method)
    # image.save('uploads/' + image_file.filename)

    return jsonify({'labels': labels, 'text': text}), 200

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 9000)))
from maps.generate_map import m # Assuming 'm' is the map object
import folium

# Create a map object centered on a location (e.g., London)
m = folium.Map(location=[51.5074, 0.1278], zoom_start=12) 

# Save the map to an HTML file
m.save("map.html")
from flask import Flask, request, jsonify, send_file, send_from_directory
import json
import os
import google.generativeai as genai

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'AIzaSyAH17rAIUWAT17_jihVOZXiBUKbcrv2D4w'

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
    app.run(port=int(os.environ.get('PORT', 9000)))
from flask import Flask, request, jsonify
from PIL import Image
from io import BytesIO
import google.cloud.vision as vision

app = Flask(__name__)

# Initialize Google Cloud Vision client (replace 'YOUR_PROJECT_ID' with your project ID)
client = vision.ImageAnnotatorClient()

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream)

    # Convert image to bytes for Cloud Vision API
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Analyze image with Cloud Vision API
    response = client.annotate_image({
        'image': {'content': img_byte_arr},
        'features': [
            {'type_': vision.Feature.Type.LABEL_DETECTION},
            {'type_': vision.Feature.Type.TEXT_DETECTION},
            # Add more features as needed (e.g., object detection, face detection)
        ]
    })

    # Extract information from response
    labels = [label.description for label in response.label_annotations]
    text = response.full_text_annotation.text

    # Store image (replace with your preferred storage method)
    # image.save('uploads/' + image_file.filename)

    return jsonify({'labels': labels, 'text': text}), 200

if __name__ == '__main__':
    app.run(debug=True)
import json
import os
import google.generativeai as genai
from flask import Flask, jsonify, request, send_file, send_from_directory

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Project IDX" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'AIzaSyAH17rAIUWAT17_jihVOZXiBUKbcrv2D4w'

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
    app.run(port=int(os.environ.get('PORT', 9000)))


