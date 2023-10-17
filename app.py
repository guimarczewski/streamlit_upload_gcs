import streamlit as st
from google.cloud import storage
import pandas as pd
import json
from google.oauth2 import service_account

# Configuração do aplicativo
st.title("Upload de Arquivos para Google Cloud Storage")
uploaded_credentials = st.file_uploader("Faça o upload do arquivo de credenciais JSON")
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
        df = pd.read_csv(uploaded_file)

        # Verifique se o arquivo tem as colunas corretas
        if set(["data", "lat", "lon", "veiculo"]).issubset(df.columns):

            # Verifique se o arquivo tem mais de 10 linhas
            if len(df) > 10:
                if storage_client is not None:
                    # Verifique se o arquivo já existe no GCS
                    bucket = storage_client.get_bucket("streamlit_upload_csv")
                    blob_name = "nome-do-arquivo-no-gcs.csv"
                    blob = bucket.blob(blob_name)

                    if blob.exists():
                        st.error("O arquivo já existe no Google Cloud Storage.")
                    else:
                        # Envie o arquivo para o Google Cloud Storage
                        blob.upload_from_file(uploaded_file)

                        # Barra de progresso
                        progress_bar = st.progress(0)
                        for percent_complete in range(100):
                            progress_bar.progress(percent_complete + 1)

                        st.success("Upload concluído com sucesso!")
                else:
                    st.error("Erro: Credenciais do Google Cloud não carregadas.")
            else:
                st.error("O arquivo deve conter mais de 10 linhas.")
        else:
            st.error("O arquivo deve ter as colunas 'data', 'lat', 'lon', 'veiculo'.")
    else:
        st.error("O arquivo deve ser um CSV.")

# Fim do seu código Streamlit
