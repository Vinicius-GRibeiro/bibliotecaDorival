import streamlit as st
import requests
import pandas as pd
from database import (
    init_db, adicionar_livro, buscar_livros,
    adicionar_aluno, listar_alunos,
    realizar_emprestimo, listar_emprestimos_ativos, realizar_devolucao
)

def buscar_dados_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
        data = response.json()
        if "items" in data:
            volume_info = data["items"][0]["volumeInfo"]
            titulo = volume_info.get("title", "")
            autores = volume_info.get("authors", ["Desconhecido"])
            return titulo, ", ".join(autores)
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar à API do Google Books: {e}")
        return None, None


st.set_page_config(page_title="Biblioteca Escolar", layout="wide")
st.title("📚 Sistema de Gerenciamento da Biblioteca Escolar")

init_db()

menu = ["Buscar Livros", "Cadastrar Livro", "Gerenciar Empréstimos", "Cadastrar Aluno"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Buscar Livros":
    st.header("Busca de Livros")
    termo_busca = st.text_input("Buscar por Título, Autor ou ISBN")
    if st.button("Buscar"):
        df_livros = buscar_livros(termo_busca)
        st.dataframe(df_livros, use_container_width=True)
    else:
        df_livros = buscar_livros()
        st.dataframe(df_livros, use_container_width=True)

elif choice == "Cadastrar Livro":
    st.header("Cadastro de Novo Livro")

    with st.form("cadastro_livro_form", clear_on_submit=True):
        isbn = st.text_input("ISBN (para busca automática)")

        if 'titulo' not in st.session_state:
            st.session_state.titulo = ""
        if 'autor' not in st.session_state:
            st.session_state.autor = ""

        if st.form_submit_button("Buscar ISBN"):
            if isbn:
                titulo_api, autor_api = buscar_dados_isbn(isbn)
                if titulo_api:
                    st.session_state.titulo = titulo_api
                    st.session_state.autor = autor_api
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
                if adicionar_livro(titulo, autor, isbn, localizacao):
                    st.success(f"Livro '{titulo}' cadastrado com sucesso!")
                    st.session_state.titulo = ""
                    st.session_state.autor = ""
                else:
                    st.error("Falha ao cadastrar o livro. Verifique se o ISBN já existe.")
            else:
                st.error("Título e Localização são campos obrigatórios.")


elif choice == "Gerenciar Empréstimos":
    st.header("Gerenciamento de Empréstimos")

    tab1, tab2 = st.tabs(["Novo Empréstimo", "Devoluções"])

    with tab1:
        st.subheader("Realizar Novo Empréstimo")

        alunos = listar_alunos()
        mapa_alunos = {f"{aluno[1]} ({aluno[2]})": aluno[0] for aluno in alunos}
        aluno_selecionado = st.selectbox("Selecione o Aluno", options=mapa_alunos.keys())

        livros_disponiveis = buscar_livros().query("Disponível == 'Sim'")
        mapa_livros = {livro['titulo']: livro['id'] for index, livro in livros_disponiveis.iterrows()}
        livro_selecionado = st.selectbox("Selecione o Livro", options=mapa_livros.keys())

        if st.button("Confirmar Empréstimo"):
            if aluno_selecionado and livro_selecionado:
                aluno_id = mapa_alunos[aluno_selecionado]
                livro_id = mapa_livros[livro_selecionado]
                realizar_emprestimo(livro_id, aluno_id)
                st.success(
                    f"Empréstimo do livro '{livro_selecionado}' para '{aluno_selecionado}' realizado com sucesso!")
                st.experimental_rerun()
            else:
                st.warning("Selecione um aluno e um livro para continuar.")

    with tab2:
        st.subheader("Registrar Devolução")
        emprestimos_ativos = listar_emprestimos_ativos()

        if not emprestimos_ativos.empty:
            for index, row in emprestimos_ativos.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(
                        f"**Livro:** {row['titulo']} | **Aluno:** {row['aluno']} | **Data:** {row['data_emprestimo']}")
                with col2:
                    if st.button("Devolver", key=f"devolver_{row['id']}"):
                        realizar_devolucao(row['id'], row['livro_id'])
                        st.success(f"Livro '{row['titulo']}' devolvido com sucesso!")
                        st.experimental_rerun()
        else:
            st.info("Nenhum empréstimo ativo no momento.")


elif choice == "Cadastrar Aluno":
    st.header("Cadastro de Aluno")
    with st.form("aluno_form", clear_on_submit=True):
        nome_aluno = st.text_input("Nome completo do aluno")
        turma_aluno = st.text_input("Turma")

        submitted_aluno = st.form_submit_button("Cadastrar Aluno")
        if submitted_aluno:
            if nome_aluno and turma_aluno:
                adicionar_aluno(nome_aluno, turma_aluno)
                st.success(f"Aluno '{nome_aluno}' cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos.")