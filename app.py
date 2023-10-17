import streamlit as st
from google.cloud import storage
import pandas as pd

# Configuração do aplicativo
st.title("Upload de Arquivos para Google Cloud Storage")
token = st.text_input("Token de Autenticação do Google Cloud")
uploaded_file = st.file_uploader("Faça o upload do arquivo CSV")

if token:
    # Inicialize o cliente do Google Cloud Storage
    storage_client = storage.Client(project="seu-projeto", credentials=token)

if uploaded_file is not None:
    # Verifique se o arquivo é um CSV
    if uploaded_file.type == 'application/vnd.ms-excel':
        df = pd.read_csv(uploaded_file)

        # Verifique se o arquivo tem as colunas corretas
        if set(["data", "lat", "lon", "veiculo"]).issubset(df.columns):

            # Verifique se o arquivo tem mais de 10 linhas
            if len(df) > 10:
                # Verifique se o arquivo já existe no GCS
                bucket = storage_client.get_bucket("seu-bucket")
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
                st.error("O arquivo deve conter mais de 10 linhas.")
        else:
            st.error("O arquivo deve ter as colunas 'data', 'lat', 'lon', 'veiculo'.")
    else:
        st.error("O arquivo deve ser um CSV.")
