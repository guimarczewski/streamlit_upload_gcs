import streamlit as st
from google.cloud import storage
import pandas as pd
import json
from google.oauth2 import service_account
import tempfile

# Configuração do aplicativo
st.title("Upload de Arquivos para Google Cloud Storage")
uploaded_credentials = st.file_uploader("Faça o upload do arquivo de credenciais JSON")

# Campo de entrada para o nome do bucket
bucket_name = st.text_input("Nome do Bucket")

uploaded_file = st.file_uploader("Faça o upload do arquivo CSV")
storage_client = None  # Inicialize o cliente do Google Cloud Storage


if uploaded_credentials is not None:
    # Verifique se o arquivo é um JSON
    if uploaded_credentials.type == 'application/json':
        try:
            # Lê as credenciais do arquivo JSON
            credentials_data = json.load(uploaded_credentials)

            # Inicialize o cliente do Google Cloud Storage com as credenciais
            credentials = service_account.Credentials.from_service_account_info(credentials_data)
            storage_client = storage.Client(credentials=credentials)
            st.success("Credenciais carregadas com sucesso!")

        except Exception as e:
            st.error(f"Erro ao carregar as credenciais: {e}")

if uploaded_file is not None:

    # Verifique se o arquivo é um CSV
    if uploaded_file.type == 'text/csv':

        # Crie um arquivo temporário para salvar o arquivo CSV
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())

        # Lê o arquivo CSV
        df = pd.read_csv(temp_file.name)

        # Verifique se o arquivo tem as colunas corretas
        if set(["data", "lat", "lon", "veiculo"]).issubset(df.columns):

            # Verifique se o arquivo tem mais de 10 linhas
            if len(df) > 10:
                if storage_client is not None:
                    # Defina o nome do objeto (arquivo) no GCS
                    blob_name = uploaded_file.name
                # Exiba as 10 primeiras linhas do arquivo CSV
                st.dataframe(df.head(10))

                    # Carregue o arquivo no GCS
                    bucket = storage_client.bucket(bucket_name)
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(temp_file.name)
                
                # Botão para fazer o upload
                if st.button("Fazer Upload"):
                    if storage_client is not None:
                        # Defina o nome do bucket e o nome do objeto (arquivo) no GCS
                        bucket_name = "streamlit_upload_csv"
                        blob_name = uploaded_file.name

                    st.success("Upload concluído com sucesso!")
                else:
                    st.error("Erro: Credenciais do Google Cloud não carregadas.")
                        # Carregue o arquivo no GCS
                        bucket = storage_client.bucket(bucket_name)
                        blob = bucket.blob(blob_name)
                        blob.upload_from_filename(temp_file.name)

                        st.success("Upload concluído com sucesso!")
                    else:
                        st.error("Erro: Credenciais do Google Cloud não carregadas.")
            else:
                st.error("O arquivo deve conter mais de 10 linhas.")
        else:
            st.error("O arquivo deve ter as colunas 'data', 'lat', 'lon', 'veiculo'.")
    else:
        st.error("O arquivo deve ser um CSV.")
# Fim do seu código
