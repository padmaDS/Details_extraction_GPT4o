import streamlit as st
import base64
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Streamlit app
st.title("Image Information Extractor")

# Language selection
language = st.selectbox("Select language", ["English", "Hindi", "Tamil", "Telugu"])

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    base64_image = encode_image(uploaded_file)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt_text = f"""Read the image and extract all information in key value pairs and document type. 
                      If address is available, divide into state, district, mandal, street etc. 
                      Language: {language}"""

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
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

    # Debugging information
    # st.write("Payload sent to API:")
    # st.json(payload)
    # st.write("Headers sent to API:")
    # st.json(headers)

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # More debugging information
        # st.write("Response status code:")
        # st.write(response.status_code)
        # st.write("Response content:")
        # st.json(response.json())

        if response.status_code == 200:
            response_data = response.json()
            message_content = response_data['choices'][0]['message']['content']
            st.success("Information extracted successfully!")
            st.write(message_content)
        else:
            st.error("Failed to extract information. Please try again.")
            st.write(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error("An error occurred while making the request.")
        st.write(str(e))
