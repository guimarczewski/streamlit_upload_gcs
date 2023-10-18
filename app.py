import streamlit as st
from google.cloud import storage
import pandas as pd
import json
from google.oauth2 import service_account
import tempfile

# Application Configuration
st.title("Upload Files to Google Cloud Storage")

# Add a sidebar to select the tab
selected_tab = st.sidebar.selectbox("Select a tab:", ["Upload File","Upload CSV with validation"])

# Initialize the Google Cloud Storage client
storage_client = None

if selected_tab == "Upload File":
    # Tab to upload without verifications

    uploaded_credentials = st.file_uploader("Upload JSON credentials file")

    # Input field for the bucket name
    bucket_name = st.text_input("Bucket Name")

    uploaded_file = st.file_uploader("Upload any file")

    if uploaded_credentials is not None:
        try:
            credentials_data = json.load(uploaded_credentials)
            credentials = service_account.Credentials.from_service_account_info(credentials_data)
            storage_client = storage.Client(credentials=credentials)

            st.success("Credentials loaded successfully!")

        except Exception as e:
            st.error(f"Error loading credentials: {e}")

    if uploaded_file is not None:
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())


        # Button to upload the file to GCS
        if st.button("Upload"):
            if storage_client is not None:
                # Set the object (file) name in GCS
                blob_name = uploaded_file.name

                try:
                    # Upload the file to GCS
                    bucket = storage_client.bucket(bucket_name)
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(temp_file.name)

                    st.success("Upload completed successfully!")
                except Exception as e:
                    # Display the error message
                    st.error(e)
            else:
                st.error("Error: Google Cloud credentials not loaded.")

if selected_tab == "Upload CSV with validation":
    # Tab with file type validation, columns and number of lines
    uploaded_credentials = st.file_uploader("Upload JSON credentials file")

    # Input field for the bucket name
    bucket_name = st.text_input("Bucket Name")

    uploaded_file = st.file_uploader("Upload CSV file")

    if uploaded_credentials is not None:
        # Check if the file is a JSON
        if uploaded_credentials.type == 'application/json':
            try:
                # Read credentials from the JSON file
                credentials_data = json.load(uploaded_credentials)

                # Initialize the Google Cloud Storage client with credentials
                credentials = service_account.Credentials.from_service_account_info(credentials_data)
                storage_client = storage.Client(credentials=credentials)

                st.success("Credentials loaded successfully!")

            except Exception as e:
                st.error(f"Error loading credentials: {e}")

    if uploaded_file is not None:
        # Check if the file is a CSV
        if uploaded_file.type == 'text/csv':

            # Create a temporary file to save the CSV file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())

            # Read the CSV file
            df = pd.read_csv(temp_file.name)

            # Check if the file has the correct columns
            if set(["data", "lat", "lon", "vehicle"]).issubset(df.columns):

                # Check if the file has more than 10 rows
                if len(df) > 10:
                    # Display the first 10 rows of the CSV file
                    st.dataframe(df.head(10))

                    # Button to upload the file
                    if st.button("Upload"):
                        if storage_client is not None:
                            # Set the object (file) name in GCS
                            blob_name = uploaded_file.name

                            try:
                                # Upload the file to GCS
                                bucket = storage_client.bucket(bucket_name)
                                blob = bucket.blob(blob_name)
                                blob.upload_from_filename(temp_file.name)

                                st.success("Upload completed successfully!")
                            except Exception as e:
                                # Display the error message
                                st.error(e)
                        else:
                            st.error("Error: Google Cloud credentials not loaded.")
                else:
                    st.error("The file must have more than 10 rows.")
            else:
                st.error("The file must have columns 'data', 'lat', 'lon', 'vehicle'.")
        else:
            st.error("The file must be a CSV.")

