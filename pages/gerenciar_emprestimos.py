import streamlit as st
from sidebar import exibir_sidebar
from database import (
    connect_and_init_db, listar_alunos, buscar_livros,
    realizar_emprestimo, listar_emprestimos_ativos, realizar_devolucao
)

st.set_page_config(page_title="Gerenciar Empréstimos", page_icon="📤")
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)

exibir_sidebar()
conn = connect_and_init_db()
st.header("📤 Gerenciamento de Empréstimos")

if conn:
    tab1, tab2 = st.tabs(["Novo Empréstimo", "Devoluções"])
    with tab1:
        st.subheader("Realizar Novo Empréstimo")
        alunos = listar_alunos(conn)
        mapa_alunos = {f"{aluno[1]} ({aluno[2]})": aluno[0] for aluno in alunos}
        aluno_selecionado = st.selectbox("Selecione o Aluno", options=mapa_alunos.keys())

        livros_disponiveis = buscar_livros(conn).query("Disponível == 'Sim'")
        mapa_livros = {livro['titulo']: livro['id'] for _, livro in livros_disponiveis.iterrows()}
        livro_selecionado = st.selectbox("Selecione o Livro", options=mapa_livros.keys())
        if st.button("Confirmar Empréstimo"):
            if aluno_selecionado and livro_selecionado:
                aluno_id = mapa_alunos[aluno_selecionado]
                livro_id = mapa_livros[livro_selecionado]
                realizar_emprestimo(conn, livro_id, aluno_id)
                st.success(f"Empréstimo do livro '{livro_selecionado}' para '{aluno_selecionado}' realizado com sucesso!")
                st.rerun()
            else:
                st.warning("Selecione um aluno e um livro para continuar.")

    with tab2:
        st.subheader("Registrar Devolução")
        emprestimos_ativos = listar_emprestimos_ativos(conn)
        if not emprestimos_ativos.empty:
            for _, row in emprestimos_ativos.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.write(f"**Livro:** {row['titulo']} | **Aluno:** {row['aluno']} | **Data:** {row['data_emprestimo']}")
                if col2.button("Devolver", key=f"devolver_{row['id']}"):
                    realizar_devolucao(conn, row['id'], row['livro_id'])
                    st.success(f"Livro '{row['titulo']}' devolvido com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum empréstimo ativo no momento.")
else:
    st.error("Não foi possível conectar ao banco de dados.")