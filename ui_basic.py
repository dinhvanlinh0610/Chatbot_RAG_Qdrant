import ui_basic as st
import requests
import os

# Set up the Streamlit page
st.set_page_config(page_title="Chatbot RAG Interface", page_icon="🤖")
st.title("RAG-Powered Chatbot For Vietnamese Marriage Law")

# Define the Flask API URLs
api_search_url = "http://localhost:5000/api/search"  # Endpoint for chatbot interaction
api_insert_url = "http://localhost:5000/api/insert_data"  # Endpoint to add documents

# Initialize session state to store chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to send user query to the Flask API and retrieve the response
def query_chatbot(user_input):
    headers = {'Content-Type': 'application/json'}
    data = [{"parts": [{"text": user_input}]}]
    try:
        response = requests.post(api_search_url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            chatbot_response = result['parts'][0]['text']
            return chatbot_response
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Function to upload file to the Flask API
def upload_file(file_path):
    headers = {'Content-Type': 'application/json'}
    data = {"data_path": file_path}  # Pass the file path as required by your backend
    try:
        response = requests.post(api_insert_url, json=data, headers=headers)
        if response.status_code == 200:
            return "Document uploaded successfully!"
        else:
            return f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Display the chat history in a scrollable box with message layout
for speaker, message in st.session_state['chat_history']:
    # Define two columns for layout
    col1, col2 = st.columns([1, 4] if speaker == "Chatbot" else [4, 1])
    
    if speaker == "You":
        with col2:  # User's message on the right
            st.markdown(f"""
                <div style='background-color: #D1ECF1; 
                padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                font-size: 16px; max-width: 100%; min-width: 100px; display: inline-block;'>
                {message}
                </div>
                """, unsafe_allow_html=True)
    else:
        with col1:  # Chatbot's message on the left
            st.markdown(f"""
                <div style='background-color: #F8D7DA; padding: 20px; 
                border-radius: 15px; margin-bottom: 20px; font-size: 16px; 
                max-width: 100%; min-width: 400px; display: inline-block;'>
                {message}
                </div>
                """, unsafe_allow_html=True)

# Input field for user to type a message (chat-like input box)
user_input = st.chat_input("Type your message...")

# If the user submits a query, process it and store both the query and response
if user_input:
    with st.spinner('Chatbot is thinking...'):
        chatbot_response = query_chatbot(user_input)
        
        # Append the user query and chatbot response to chat history
        st.session_state['chat_history'].append(("You", user_input))
        st.session_state['chat_history'].append(("Chatbot", chatbot_response))

    # Scroll to the bottom of the chat box (optional if you want to keep latest messages visible)
    st.experimental_rerun()  # This will automatically update the chat history after each new message

# Sidebar section for uploading documents
st.sidebar.subheader("Upload a CSV Document for Insertion")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# If a file is uploaded, handle the upload
if uploaded_file:
    # Save the uploaded file to a temporary location
    temp_file_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    # Send the file path to the backend API
    with st.spinner('Uploading document...'):
        upload_result = upload_file(temp_file_path)
    
    st.sidebar.success(upload_result)

# Optionally, a button to clear the chat
if st.sidebar.button("Clear Chat"):
    st.session_state['chat_history'] = []
