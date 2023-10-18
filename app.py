import streamlit as st
from google.cloud import storage
import pandas as pd
import json
from google.oauth2 import service_account
import tempfile

class GoogleCloudUploader:
    def __init__(self):
        st.title("Upload Files to Google Cloud Storage")
        self.storage_client = None

    def load_credentials(self, uploaded_credentials):
        try:
            credentials_data = json.load(uploaded_credentials)
            credentials = service_account.Credentials.from_service_account_info(credentials_data)
            self.storage_client = storage.Client(credentials=credentials)
            st.success("Credentials loaded successfully!")
        except Exception as e:
            st.error(f"Error loading credentials: {e}")

    def upload_file(self, bucket_name, uploaded_file):
        if self.storage_client is not None:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                
            blob_name = uploaded_file.name
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if blob.exists():
                replace_existing = st.checkbox("The file already exists. Do you want to replace it?")
                if not replace_existing:
                    st.warning("Upload canceled. The existing file will not be replaced.")
                else:
                    try:
                        blob.upload_from_filename(temp_file.name)
                        st.success("Upload completed successfully!")
                    except Exception as e:
                        st.error(e)
            else:
                try:
                    blob.upload_from_filename(temp_file.name)
                    st.success("Upload completed successfully!")
                except Exception as e:
                    st.error(e)
        else:
            st.error("Error: Google Cloud credentials not loaded")

class UploadFileTab:
    def __init__(self, uploader):
        self.uploader = uploader
        uploaded_credentials = st.file_uploader("Upload JSON credentials file")
        bucket_name = st.text_input("Bucket Name")
        uploaded_file = st.file_uploader("Upload any file")

        if uploaded_credentials:
            self.uploader.load_credentials(uploaded_credentials)

        if uploaded_file:
            if st.button("Upload"):
                self.uploader.upload_file(bucket_name, uploaded_file)

class UploadCSVTab:
    def __init__(self, uploader):
        self.uploader = uploader
        uploaded_credentials = st.file_uploader("Upload JSON credentials file")
        bucket_name = st.text_input("Bucket Name")
        uploaded_file = st.file_uploader("Upload CSV file")

        if uploaded_credentials:
            self.uploader.load_credentials(uploaded_credentials)

        if uploaded_file:
            if st.button("Upload"):
                self.uploader.upload_file(bucket_name, uploaded_file)

def main():
    selected_tab = st.sidebar.selectbox("Select a tab:", ["Upload File", "Upload CSV with validation"])
    uploader = GoogleCloudUploader()

    if selected_tab == "Upload File":
        UploadFileTab(uploader)
    elif selected_tab == "Upload CSV with validation":
        UploadCSVTab(uploader)

if __name__ == "__main__":
    main()
