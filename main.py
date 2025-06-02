from flask import Flask, request, jsonify, send_file, send_from_directory
import json
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import google.cloud.vision as vision
import googlemaps
from google.cloud import aiplatform

# Initialize Flask App
app = Flask(__name__)

# Initialize Google Cloud clients
# Gemini API client
aiplatform.init(project='lateral-avatar-413022', location='us-central1')
# Google Cloud Vision client
client = vision.ImageAnnotatorClient() # (replace 'YOUR_PROJECT_ID' with your project ID) - project id seems to be set by aiplatform.init, so this comment might be outdated

# API Key Configuration
# Google Maps API Key
google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=google_maps_api_key)

# Gemini API Key
API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)


@app.route('/api/restaurants', methods=['POST'])
def get_restaurants():
    location = request.json.get('location')
    if not location:
        return jsonify({'error': 'Missing location'}), 400

    # Use the Google Maps Places API to search for restaurants
    places_result = gmaps.places_nearby(
        location=location,
        type='restaurant',
        radius=5000  # Search within a 5km radius
    )

    restaurants = []
    for place in places_result['results']:
        restaurants.append({
            'name': place['name'],
            'place_id': place['place_id'],
            'address': place['vicinity'],
            'rating': place['rating']
        })

    return jsonify({'restaurants': restaurants})

@app.route('/api/chat', methods=['POST'])
def chat():
    # TODO: This route is currently a placeholder and needs full implementation
    # to handle chat logic with restaurant context.
    message = request.json.get('message')
    restaurant_name = request.json.get('restaurant_name')  # Get restaurant context

    if not message or not restaurant_name:
        return jsonify({'error': 'Missing message or restaurant name'}), 400

@app.route('/api/generate_text', methods=['POST'])
def generate_text():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'Missing prompt'}), 400

    # Use the Gemini API to generate text
    # TODO: Replace 'your-endpoint-name' with your actual deployed Vertex AI Endpoint name.
    endpoint = aiplatform.Endpoint('your-endpoint-name')
    response = endpoint.predict(instances=[{'text': prompt}])
    generated_text = response.predictions[0]['text']

    return jsonify({'text': generated_text})

# Serve the main index page
@app.route("/")
def index():
    return send_file('web/index.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if not API_KEY: # Check if API_KEY is not set (empty or None)
            return jsonify({ "error": '''
                To get started, get an API key for Gemini at
                https://g.co/ai/idxGetGeminiKey and set it as an environment variable named GEMINI_API_KEY.
                Then, add the environment variable to your run configuration in Project IDX.
                '''.replace('\n', '').strip() })
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

if __name__ == '__main__': # Consolidated main execution block
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
