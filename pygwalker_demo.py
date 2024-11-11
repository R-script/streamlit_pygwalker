from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st

# Function to load data from selected file
def load_data(file):
    if file is not None:
        # Load CSV files
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        # Load Excel files
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
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
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

        # Load Data
        if uploaded_file is not None:
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
        pyg_app = StreamlitRenderer(df)
 
        pyg_app.explorer() 
        

        # Button to go back to upload screen
        if st.button("Go Back to Upload"):
            st.session_state.data = None  # Reset session state for data
            st.session_state.visualization = False

if __name__ == "__main__":
    main()