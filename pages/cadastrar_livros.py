import streamlit as st
import requests
from sidebar import exibir_sidebar
from database import connect_and_init_db, adicionar_livro

st.set_page_config(page_title="Cadastrar Livro", page_icon="📖")
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)

exibir_sidebar()

def buscar_dados_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "items" in data:
            volume_info = data["items"][0]["volumeInfo"]
            titulo = volume_info.get("title", "")
            autores = volume_info.get("authors", ["Desconhecido"])
            return titulo, ", ".join(autores)
        return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar à API do Google Books: {e}")
        return None, None

conn = connect_and_init_db()
st.header("📖 Cadastro de Novo Livro")

if conn:
    with st.form("cadastro_livro_form", clear_on_submit=True):
        isbn = st.text_input("ISBN (para busca automática)")
        if 'titulo' not in st.session_state: st.session_state.titulo = ""
        if 'autor' not in st.session_state: st.session_state.autor = ""

        if st.form_submit_button("Buscar ISBN"):
            if isbn:
                titulo_api, autor_api = buscar_dados_isbn(isbn)
                if titulo_api:
                    st.session_state.titulo, st.session_state.autor = titulo_api, autor_api
                    st.success("Dados do livro encontrados!")
                else:
                    st.warning("ISBN não encontrado. Preencha os dados manualmente.")
            else:
                st.warning("Por favor, insira um ISBN.")

        titulo = st.text_input("Título", value=st.session_state.titulo)
        autor = st.text_input("Autor(es)", value=st.session_state.autor)
        localizacao = st.text_input("Localização (Ex: A1, B3, C2)", placeholder="Ex: A1")
        submitted = st.form_submit_button("Cadastrar Livro")

        if submitted:
            if titulo and localizacao:
                if adicionar_livro(conn, titulo, autor, isbn, localizacao):
                    st.success(f"Livro '{titulo}' cadastrado com sucesso!")
                    st.session_state.titulo, st.session_state.autor = "", ""
                else:
                    st.error("Falha ao cadastrar o livro. Verifique se o ISBN já existe.")
            else:
                st.error("Título e Localização são campos obrigatórios.")
else:
    st.error("Não foi possível conectar ao banco de dados.")