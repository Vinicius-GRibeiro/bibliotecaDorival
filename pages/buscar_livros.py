import streamlit as st
from sidebar import exibir_sidebar
from database import connect_and_init_db, buscar_livros

st.set_page_config(page_title="Buscar Livros", page_icon="🔎")
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)

exibir_sidebar()
conn = connect_and_init_db()

st.header("🔎 Busca de Livros")

if conn:
    termo_busca = st.text_input("Buscar por Título, Autor ou ISBN")
    df_livros = buscar_livros(conn, termo_busca)
    st.dataframe(df_livros, use_container_width=True, hide_index=True)
else:
    st.error("Não foi possível conectar ao banco de dados.")