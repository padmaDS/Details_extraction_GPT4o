
## All the information in sidebar

import streamlit as st
import base64
import requests
import json
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Function to download as text file
def download_text(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download as .txt</a>'
    return href

# Function to download as JSON file
def download_json(data, filename):
    try:
        # Encode the extracted JSON data
        b64 = base64.b64encode(json.dumps(data).encode()).decode()
        # Create download link
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Download as .json</a>'
        return href
    except Exception as e:
        # Return error message if an exception occurs
        return f"Error: {str(e)}"

# Function to download as CSV file
def download_csv(data, filename):
    csv_data = ",".join(data.keys()) + "\n" + ",".join(data.values())
    b64 = base64.b64encode(csv_data.encode()).decode()
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}">Download as .csv</a>'
    return href

# Streamlit app
st.title("AR Smart App")

# Document type selection
document_type_options = ["Aadhaar Card", "PAN Card", "Ration Card", "Passport", "Driving Licence", "Voter ID", "Bank Cheque", "Electricity Bill", "Other", "KYC", "Invoice/Bills", "Indian Tax Forms", "US Tax Forms"]
document_type = st.sidebar.selectbox("Select Document Type", document_type_options)

# Language selection
language = st.selectbox("Select language", ["English", "Hindi", "Telugu", "Tamil" , "Spanish", "French", "German"])

input_type = st.sidebar.radio("Choose Input Type:", ("Local File", "URL"))

if input_type == "Local File":
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        base64_image = encode_image(uploaded_file)
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

elif input_type == "URL":
    image_url = st.sidebar.text_input("Enter the image URL:")

if st.sidebar.button("Extract Information"):
    if input_type == "Local File" or input_type == "URL":
        if input_type == "Local File":
            base64_image = encode_image(uploaded_file)
            # st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        elif input_type == "URL":
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    # st.image(image, caption="Uploaded Image", use_column_width=True)
                    base64_image = encode_image(BytesIO(response.content))
                else:
                    st.error("Failed to fetch image from the provided URL.")
                    st.stop()
            except Exception as e:
                st.error("An error occurred while fetching the image.")
                st.write(str(e))
                st.stop()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        prompt_text = f"""Read the image and extract all information in key value pairs and document type
                        in {language} language. 
                        If address is available, divide into state, district, mandal, street etc. 
                          """

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
            "max_tokens": 1000
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                if response.content:
                    response_data = response.json()
                    message_content = response_data['choices'][0]['message']['content']
                    st.success("Information extracted successfully!")
                    # st.write(message_content)

                    st.session_state.extracted_content = message_content
                else:
                    st.error("Failed to extract information. Please try again.")
                    st.write(f"Empty response received from the API.")
            else:
                st.error(f"Failed to make the request. Status Code: {response.status_code}")
                st.write(response.text)

        except Exception as e:
            st.error("An error occurred while making the request.")
            st.write(str(e))

if 'extracted_content' in st.session_state:
    extracted_content = st.session_state.extracted_content

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Uploaded Image / Image URL:")
        if input_type == "Local File":
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        elif input_type == "URL":
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                else:
                    st.error("Failed to fetch image from the provided URL.")
            except Exception as e:
                st.error("An error occurred while fetching the image.")
                st.write(str(e))

    with col2:
        st.subheader("Extracted Data:")
        st.write(extracted_content)

    st.subheader("Download Output:")
    download_format = st.selectbox("Select Download Format", ["Text", "JSON", "CSV"])
    if download_format == "Text":
        st.markdown(download_text(extracted_content, "output.txt"), unsafe_allow_html=True)
    elif download_format == "JSON":
        st.markdown(download_json(json.loads(extracted_content), "output.json"), unsafe_allow_html=True)
    elif download_format == "CSV":
        st.markdown(download_csv({"Extracted Data": extracted_content}, "output.csv"), unsafe_allow_html=True)
