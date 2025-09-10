import streamlit as st

def exibir_sidebar():
    with st.sidebar:
        st.header("Biblioteca Escolar")
        st.page_link("app.py", label="Início", icon="🏠")
        st.page_link("pages/buscar_Livros.py", label="Buscar Livros", icon="🔎")
        st.page_link("pages/cadastrar_livros.py", label="Cadastrar Livro", icon="📖")
        st.page_link("pages/gerenciar_emprestimos.py", label="Empréstimos", icon="📤")
        st.page_link("pages/cadastrar_aluno.py", label="Alunos", icon="👨‍🎓")
        st.markdown("---")
        st.info("Sistema de gerenciamento da biblioteca.")