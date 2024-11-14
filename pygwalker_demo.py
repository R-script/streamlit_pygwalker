import pandas as pd
import streamlit as st
import requests
from pygwalker.api.streamlit import StreamlitRenderer

# Define the FastAPI upload endpoint URL
FASTAPI_UPLOAD_URL = "http://127.0.0.1:8000/upload"

# Function to load data based on file type
def load_data(file_path, file_type):
    # Load CSV files
    if file_type == 'csv':
        return pd.read_csv(file_path)
    # Load Excel files
    elif file_type == 'xlsx':
        return pd.read_excel(file_path)
    return None

# Main application function
def main():
    # Initialize session state for the uploaded data
    if 'data' not in st.session_state:
        st.session_state.data = None

    # Step 1: File Upload Section
    if st.session_state.data is None:
        st.title("Data Upload Screen")
        st.header("Upload your data file")
        
        # Use Streamlit's file uploader
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

        # Upload file to FastAPI if a file is chosen
        if uploaded_file is not None:
            # Send file to FastAPI
            with st.spinner("Uploading file..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(FASTAPI_UPLOAD_URL, files=files)

                if response.status_code == 200:
                    # Load the data returned by FastAPI
                    file_path = response.json().get("file_path")
                    file_type = uploaded_file.name.split('.')[-1]
                    data = load_data(file_path, file_type)

                    if data is not None:
                        st.session_state.data = data  # Store data in session state
                        st.success("File uploaded successfully!")
                        st.write("Here is a preview of your data:")
                        st.dataframe(data)

                        # Button to navigate to visualization
                        if st.button("Proceed to Visualization"):
                            st.session_state.visualization = True
                    else:
                        st.error("Error loading the file. Please ensure it's a valid CSV or Excel file.")
                else:
                    st.error("Failed to upload file. Please try again.")
    else:
        # Step 2: Data Visualization Screen
        st.set_page_config(
            page_title="Use Pygwalker In Streamlit",
            layout="wide"
        )
        df = st.session_state.data
        pyg_app = StreamlitRenderer(df)
        pyg_app.explorer() 

        # Button to go back to upload screen
        if st.button("Go Back to Upload"):
            st.session_state.data = None  # Reset session state for data
            st.session_state.visualization = False

if __name__ == "__main__":
    main()
