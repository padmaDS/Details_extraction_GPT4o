import base64
import requests
import json
import os
import urllib.parse
import requests
import base64
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = r"data\aadhar_back.jpg"
# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": f"""Read the image and extract all information in key value pairs and document type. Do not keep, Here’s the information extracted from the image in key-value pairs, in the beginning:
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

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

response_data = json.loads(response.content)

# Extract relevant details
message_content = response_data['choices'][0]['message']['content']

# Print relevant details
print(message_content)