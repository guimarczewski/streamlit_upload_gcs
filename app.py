import streamlit as st
from google.cloud import storage
import pandas as pd
import json

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

            # Verifique se as credenciais têm as informações necessárias (project_id, private_key, client_email)
            required_fields = ["project_id", "private_key", "client_email"]
            if all(field in credentials_data for field in required_fields):
                # Crie as credenciais compatíveis com google-auth-library-python
                credentials = {
                    "project_id": credentials_data["project_id"],
                    "private_key": credentials_data["private_key"],
                    "client_email": credentials_data["client_email"],
                }

                # Inicialize o cliente do Google Cloud Storage com as credenciais
                storage_client = storage.Client(credentials=credentials)

                st.success("Credenciais carregadas com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar as credenciais: {e}")

if uploaded_file is not None:
    # Exiba as 10 primeiras linhas do arquivo
    st.subheader("Visualização das 10 Primeiras Linhas:")
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head(10))

    # Botão para enviar o arquivo
    if st.button("Enviar para o Google Cloud Storage"):
        if storage_client is not None:
            # Resto do código para envio do arquivo
            # ...

            st.success("Upload concluído com sucesso!")

# Fim do seu código Streamlit
