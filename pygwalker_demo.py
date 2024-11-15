import pandas as pd
import numpy as np
import streamlit as st
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from io import BytesIO
from pygwalker.api.streamlit import StreamlitRenderer

# FastAPI app setup
fastapi_app = FastAPI()

# Set up CORS to allow requests from Streamlit
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin to make requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI endpoint for file upload
@fastapi_app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Here you can add your file processing logic, like saving or parsing the file
    return {"filename": file.filename, "content_type": file.content_type}

# Function to run FastAPI in a background thread
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

# Start FastAPI in a background thread
threading.Thread(target=run_fastapi, daemon=True).start()

# Function to load data from the uploaded file (CSV or Excel)
def load_data(file):
    if file is not None:
        # Load CSV files
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        # Load Excel files
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
    return None

# Function to upload file to FastAPI
def upload_to_fastapi(file):
    url = "http://127.0.0.1:8000/upload"  # FastAPI local URL
    file_bytes = BytesIO(file.read())  # Read file as bytes
    files = {'file': (file.name, file_bytes, file.type)}
    response = requests.post(url, files=files)
    return response.json()

# Function to preprocess data before passing it to pygwalker
def preprocess_data(df):
    """Clean and preprocess the data before passing it to pygwalker."""
    
    # Replace None or NaN values with NaN or a placeholder
    df = df.applymap(lambda x: np.nan if x is None else x)
    
    # Optionally, fill NaN values with a placeholder, for example, 0 or "N/A"
    df = df.fillna("N/A")  # Or you could use 0, depending on the data

    # Alternatively, you can drop rows/columns with NaN values
    # df = df.dropna()  # Uncomment this line to drop rows with NaN values
    
    # Limit the dataset size to a manageable number of rows (e.g., 1000 rows)
    max_rows = 1000
    df = df.head(max_rows)
    
    return df

# Main Streamlit application function
def main():
    # Initialize session state for the uploaded data
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'visualization' not in st.session_state:
        st.session_state.visualization = False

    # Step 1: File Upload Section
    if not st.session_state.visualization:
        st.title("Data Upload Screen")
        st.header("Upload your data file")
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

        # Load Data
        if uploaded_file is not None:
            # Upload the file to FastAPI server for processing
            response = upload_to_fastapi(uploaded_file)
            st.write(response)  # Show the response from FastAPI

            # Load the data into the Streamlit app
            data = load_data(uploaded_file)

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
        # Step 2: Data Visualization Screen
        st.set_page_config(
            page_title="Use Pygwalker In Streamlit",
            layout="wide"
        )
        df = st.session_state.data

        # Preprocess the data before passing it to pygwalker
        df = preprocess_data(df)

        try:
            pyg_app = StreamlitRenderer(df)
            pyg_app.explorer()  # Visualize the data
        except Exception as e:
            st.error(f"An error occurred while visualizing the data: {e}")

        # Button to go back to upload screen
        if st.button("Go Back to Upload"):
            st.session_state.data = None  # Reset session state for data
            st.session_state.visualization = False  # Reset visualization state

# Run the main function to start the app
if __name__ == "__main__":
    main()
