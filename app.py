###
# Its findining the document type along with all the document details
###

import os
import base64
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image to base64
def encode_image_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    else:
        return None

@app.route('/kyc', methods=['POST'])
def extract_info():
    # Check if JSON payload is provided
    if not request.json:
        return jsonify({"error": "No JSON payload provided"}), 400

    # Check if image URL is provided in the JSON payload
    if 'image_url' not in request.json:
        return jsonify({"error": "No image URL provided"}), 400

    image_url = request.json['image_url']
    language = request.json['language']

    base64_image = encode_image_from_url(image_url)

    if base64_image is None:
        return jsonify({"error": "Failed to fetch image from URL"}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",  # Replace with the actual model name
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Read the image and extract all information in key value pairs and document type in tamil language. Do not keep, Here’s the information extracted from the image in key-value pairs, in the begining:
                                   if address is available, divide into state, district, mandal, street etc.
                                   Ensuring there are no newline characters between the pairs. The key-value pairs should be separated by commas:
                                   """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Make the request to OpenAI API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    # Extract relevant details from the response
    if 'choices' in response_data and len(response_data['choices']) > 0:
        message_content = response_data['choices'][0]['message']['content']
        return jsonify({"document_details": message_content})
    else:
           return jsonify({                
                "document_type": "Unknown",
                "Name": "",
                "Fathers Name": "",
                "Date of Birth": "",
                "Aadhar Number": "",
                "Pan Number": "",
                "Check Details": "",
                "Ration card Details": ""
            }), 500

if __name__ == '__main__':
    app.run(debug=True)
