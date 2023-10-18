# streamlit_upload_gcs

Streamlit App created for uploading files to Google Cloud Storage.
Available at https://cloud-upload-files.streamlit.app/

To perform the upload, you will need:

- A JSON file containing the credentials of a service account with editor access to Cloud Storage. The step-by-step guide to creating it is available at https://developers.google.com/workspace/guides/create-credentials?hl=en#service-account
- The name of the Bucket where the file will be sent. The Bucket must already be created.

Regarding the file, for this project, the following requirements have been defined:
- The file must be in CSV format.
- It must contain the following columns: 'data,' 'lat,' 'lon,' and 'vehicle.'
- It must have more than 10 lines to avoid sending empty files.
These configurations can be modified in the app.py file and a model its in data folder.

After loading the file, a preview with the first 10 lines is displayed for confirmation, followed by the "Upload" button.

Next project steps:
- Integration with AWS and Azure
- Analysis of the uploaded data: number of rows, null values...
- Slack message when the file is sent

Additionally, a new tab has been added to enable the upload of files of any type with no verifications.
