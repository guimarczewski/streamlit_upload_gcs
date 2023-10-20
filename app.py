import streamlit as st
import pandas as pd
import json
import tempfile
from google.cloud import storage
from google.oauth2 import service_account
from st_files_connection import FilesConnection
import boto3

class AmazonS3Uploader:
    def __init__(self):
        st.title("Upload Files to Amazon S3")
        self.s3_client = FilesConnection('s3')

    def load_credentials(self):
        self.s3_client.set_credentials()

    def upload_file(self, bucket_name, uploaded_file):
        if self.s3_client is not None:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())

            blob_name = uploaded_file.name
            bucket = self.s3_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if blob.exists():
                st.warning("The file already exists. Do you want to replace it?")
                replace_existing = st.button("Replace")
                cancel_upload = st.button("Cancel")

                if replace_existing:
                    try:
                        blob.upload_from_filename(temp_file.name)
                        st.success("Upload to Amazon S3 completed successfully!")
                    except Exception as e:
                        st.error(e)
                elif cancel_upload:
                    st.warning("Upload to Amazon S3 canceled. The existing file will not be replaced.")
            else:
                try:
                    blob.upload_from_filename(temp_file.name)
                    st.success("Upload to Amazon S3 completed successfully!")
                except Exception as e:
                    st.error(e)
        else:
            st.error("Error: Amazon S3 credentials not loaded")

class GoogleCloudUploader:
    def __init__(self):
        st.title("Upload Files to Google Cloud Storage")
        self.storage_client = None

    def load_credentials(self, uploaded_credentials):
        try:
            credentials_data = json.load(uploaded_credentials)
            credentials = service_account.Credentials.from_service_account_info(credentials_data)
            self.storage_client = storage.Client(credentials=credentials)
            st.success("Google Cloud credentials loaded successfully!")
        except Exception as e:
            st.error(f"Error loading Google Cloud credentials: {e}")

    def upload_file(self, bucket_name, uploaded_file):
        if self.storage_client is not None:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                
            blob_name = uploaded_file.name
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if blob.exists():
                st.warning("The file already exists. Do you want to replace it?")
                replace_existing = st.button("Replace")
                cancel_upload = st.button("Cancel")

                if replace_existing:
                    try:
                        blob.upload_from_filename(temp_file.name)
                        st.success("Upload to Google Cloud completed successfully!")
                    except Exception as e:
                        st.error(e)
                elif cancel_upload:
                    st.warning("Upload to Google Cloud canceled. The existing file will not be replaced.")
            else:
                try:
                    blob.upload_from_filename(temp_file.name)
                    st.success("Upload to Google Cloud completed successfully!")
                except Exception as e:
                    st.error(e)
        else:
            st.error("Error: Google Cloud credentials not loaded")

class UploadFileTab_gcs:
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

class UploadCSVTab_gcs:
    def __init__(self, uploader):
        self.uploader = uploader
        uploaded_credentials = st.file_uploader("Upload JSON credentials file")
        bucket_name = st.text_input("Bucket Name")
        uploaded_file = st.file_uploader("Upload CSV file")

        if uploaded_credentials:
            self.uploader.load_credentials(uploaded_credentials)

        if uploaded_file:
            error_type = self.validate_csv_file(uploaded_file)
            if error_type is not True:
                self.show_error_message(error_type)
            else:
                if st.button("Upload"):
                    self.uploader.upload_file(bucket_name, uploaded_file)

    def validate_csv_file(self, uploaded_file):
        # Verifique se a extensão do arquivo é `.csv`.
        if not uploaded_file.name.endswith(".csv"):
            return "invalid_extension"

        # Verifique se o arquivo contém as colunas `data`, `lat`, `lon`, `vehicle`.
        try:
            df = pd.read_csv(uploaded_file)
            if not all(col in df.columns for col in ["data", "lat", "lon", "vehicle"]):
                return "missing_columns"
        except Exception as e:
            pass

        # Verifique se o arquivo contém mais de 10 linhas.
        if len(df) <= 10:
            return "too_few_rows"

        return True

    def show_error_message(self, error_type):
        if error_type == "invalid_extension":
            st.error("The file must be a CSV file.")
        elif error_type == "missing_columns":
            st.error("The CSV file must contain the following columns: data, lat, lon, vehicle.")
        elif error_type == "too_few_rows":
            st.error("The CSV file must contain at least 11 rows.")

class UploadFileTab_aws:
    def __init__(self, uploader):
        self.uploader = uploader
        aws_access_key_id_input = st.text_input("AWS Access Key ID")
        aws_secret_access_key_input = st.text_input("AWS Secret Access Key", type="password")
        bucket_name = st.text_input("Bucket Name")
        uploaded_file = st.file_uploader("Upload any file")

        if uploaded_file:
            if st.button("Upload"):
                s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id_input, aws_secret_access_key=aws_secret_access_key_input)
                s3.Object(bucket_name, uploaded_file.name).put(Body=uploaded_file.read())

class UploadCSVTab_aws:
    def __init__(self, uploader):
        self.uploader = uploader
        aws_access_key_id_input = st.text_input("AWS Access Key ID")
        aws_secret_access_key_input = st.text_input("AWS Secret Access Key", type="password")
        bucket_name = st.text_input("Bucket Name")
        uploaded_file = st.file_uploader("Upload CSV file")

        if uploaded_file:
            error_type = self.validate_csv_file(uploaded_file)
            if error_type is not True:
                self.show_error_message(error_type)
            else:
                if st.button("Upload"):
                    s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id_input, aws_secret_access_key=aws_secret_access_key_input)
                    s3.Object(bucket_name, uploaded_file.name).put(Body=uploaded_file.read())

    def validate_csv_file(self, uploaded_file):
        # Verifique se a extensão do arquivo é `.csv`.
        if not uploaded_file.name.endswith(".csv"):
            return "invalid_extension"

        # Verifique se o arquivo contém as colunas `data`, `lat`, `lon`, `vehicle`.
        try:
            df = pd.read_csv(uploaded_file)
            if not all(col in df.columns for col in ["data", "lat", "lon", "vehicle"]):
                return "missing_columns"
        except Exception as e:
            pass

        # Verifique se o arquivo contém mais de 10 linhas.
        if len(df) <= 10:
            return "too_few_rows"

        return True

    def show_error_message(self, error_type):
        if error_type == "invalid_extension":
            st.error("The file must be a CSV file.")
        elif error_type == "missing_columns":
            st.error("The CSV file must contain the following columns: data, lat, lon, vehicle.")
        elif error_type == "too_few_rows":
            st.error("The CSV file must contain at least 11 rows.")

def main():

    selected_tab_cloud = st.sidebar.selectbox("Select a Cloud:", ["AWS S3", "Google Cloud Storage"])

    if selected_tab_cloud == "Google Cloud Storage":
        uploader = GoogleCloudUploader()
    elif selected_tab_cloud == "AWS S3":
        uploader = AmazonS3Uploader()
        
    selected_tab = st.sidebar.selectbox("Select a tab:", ["Upload File", "Upload CSV with validation"])

    if selected_tab == "Upload File" and selected_tab_cloud == "Google Cloud Storage":
        UploadFileTab_gcs(uploader)
    elif selected_tab == "Upload CSV with validation" and selected_tab_cloud == "Google Cloud Storage":
        UploadCSVTab_gcs(uploader)
    elif selected_tab == "Upload File" and selected_tab_cloud == "AWS S3":
        UploadFileTab_aws(uploader)
    elif selected_tab == "Upload CSV with validation" and selected_tab_cloud == "AWS S3":
        UploadCSVTab_aws(uploader)

if __name__ == "__main__":
    main()
