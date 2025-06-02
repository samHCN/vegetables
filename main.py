from flask import Flask, request, jsonify, send_file, send_from_directory
import json
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import google.cloud.vision as vision
import googlemaps
from google.cloud import aiplatform
from google.cloud import firestore

app = Flask(__name__)

# Initialize Google Cloud services
aiplatform.init(project='lateral-avatar-413022', location='us-central1')
client = vision.ImageAnnotatorClient() # For Vision API
db = firestore.Client() # For Firestore

# API Keys
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

# Initialize Google Maps Places API client
if not google_maps_api_key:
    print("Warning: GOOGLE_MAPS_API_KEY is not set. The /api/restaurants endpoint may not work as expected.")
gmaps = googlemaps.Client(key=google_maps_api_key)

# Configure Gemini API
if GEMINI_API_KEY and GEMINI_API_KEY != 'TODO':
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY is not set or is 'TODO'. The /api/generate endpoint will not work.")

@app.route('/api/restaurants', methods=['POST'])
def get_restaurants():
    if not google_maps_api_key:
        return jsonify({'error': 'Google Maps API key not configured'}), 500

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

@app.route('/api/chat', methods=['POST', 'GET'])
def chat_api():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
        text = data.get('text')

        if not user_id or not text:
            return jsonify({'error': 'Missing user_id or text'}), 400

        chat_ref = db.collection('chats').document()
        chat_ref.set({
            'user_id': user_id,
            'text': text,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({'success': True, 'message_id': chat_ref.id}), 201
    
    elif request.method == 'GET':
        messages_query = db.collection('chats').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20)
        messages = []
        for doc in messages_query.stream():
            msg = doc.to_dict()
            msg['id'] = doc.id
            # Convert timestamp to string if needed for JSON serialization
            if msg.get('timestamp') and hasattr(msg['timestamp'], 'isoformat'):
                 msg['timestamp'] = msg['timestamp'].isoformat()
            elif msg.get('timestamp'):
                 msg['timestamp'] = str(msg['timestamp'])
            messages.append(msg)
        messages.reverse() # To get them in chronological order
        return jsonify(messages), 200

# TODO: This requires a valid Vertex AI endpoint and further setup.
# @app.route('/api/generate_text', methods=['POST'])
# def generate_text():
#     prompt = request.json.get('prompt')
#     if not prompt:
#         return jsonify({'error': 'Missing prompt'}), 400
#
#     # Use the Gemini API to generate text
#     endpoint = aiplatform.Endpoint('your-endpoint-name')
#     response = endpoint.predict(instances=[{'text': prompt}])
#     generated_text = response.predictions[0]['text']
#
#     return jsonify({'text': generated_text})

@app.route("/")
def index():
    return send_file('web/index.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if not GEMINI_API_KEY or GEMINI_API_KEY == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key by selecting "Add Gemini API" 
                in the "Project IDX" panel in the sidebar or by visiting 
                https://g.co/ai/idxGetGeminiKey and set it as the GEMINI_API_KEY
                environment variable.
                '''.replace('\n', '').replace('                ', ' ') })
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

# Serve static files from 'web' directory
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
