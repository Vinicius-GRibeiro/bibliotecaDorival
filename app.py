# app.py
import streamlit as st
from dotenv import load_dotenv
from sidebar import exibir_sidebar
from database import connect_and_init_db

load_dotenv()

st.set_page_config(
    page_title="Início | Biblioteca Escolar",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

exibir_sidebar()

conn = connect_and_init_db()

st.title("📚 Sistema de Gerenciamento da Biblioteca")
st.header("Bem-vindo(a)!")

if conn:
    st.success("Conexão com o banco de dados estabelecida com sucesso!")
    st.info("Utilize a barra de navegação à esquerda para gerenciar o sistema.")
else:
    st.error("Falha na conexão com o banco de dados. Verifique o arquivo .env e a rede.")