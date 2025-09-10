import streamlit as st
from sidebar import exibir_sidebar
from database import connect_and_init_db, adicionar_aluno, listar_alunos

st.set_page_config(page_title="Cadastrar Aluno", page_icon="👨‍🎓")
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)

exibir_sidebar()
conn = connect_and_init_db()
st.header("👨‍🎓 Cadastro de Aluno")

if conn:
    tab1, tab2 = st.tabs(["Visualizar Alunos", "Cadastrar Novo Aluno"])

    with tab1:
        st.subheader("Alunos Cadastrados")
        alunos_data = listar_alunos(conn)
        if alunos_data:
            st.dataframe(alunos_data, use_container_width=True, header=["ID", "Nome", "Turma"], hide_index=True)
        else:
            st.info("Nenhum aluno cadastrado.")

    with tab2:
        st.subheader("Cadastrar Novo Aluno")
        with st.form("aluno_form", clear_on_submit=True):
            nome_aluno = st.text_input("Nome completo do aluno")
            turma_aluno = st.text_input("Turma")
            if st.form_submit_button("Cadastrar Aluno"):
                if nome_aluno and turma_aluno:
                    adicionar_aluno(conn, nome_aluno, turma_aluno)
                    st.success(f"Aluno '{nome_aluno}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos.")
else:
    st.error("Não foi possível conectar ao banco de dados.")