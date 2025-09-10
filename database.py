# database.py
import streamlit as st
import libsql_client
import pandas as pd
from datetime import date
import os

def get_connection():
    try:
        url = os.getenv("TURSO_DB_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")

        if not url or not auth_token:
            st.error("As credenciais do banco de dados (TURSO_DB_URL, TURSO_AUTH_TOKEN) não foram encontradas.")
            st.warning("Verifique se o seu arquivo .env está na raiz do projeto e foi carregado corretamente.")
            return None

        if url.startswith("https://"):
            url = url.replace("https://", "libsql://", 1)

        client = libsql_client.create_client_sync(
            url=url,
            auth_token=auth_token
        )
        return client
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

@st.cache_resource
def connect_and_init_db():
    connection = get_connection()
    if connection:
        init_db(connection)
    return connection

def init_db(client):
    """Inicializa as tabelas do banco de dados usando a conexão fornecida."""
    if not client: return
    client.batch([
        "CREATE TABLE IF NOT EXISTS livros (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, autor TEXT, isbn TEXT UNIQUE, localizacao TEXT NOT NULL, disponivel BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS alunos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, turma TEXT)",
        "CREATE TABLE IF NOT EXISTS emprestimos (id INTEGER PRIMARY KEY, livro_id INTEGER, aluno_id INTEGER, data_emprestimo DATE, data_devolucao DATE, FOREIGN KEY(livro_id) REFERENCES livros(id), FOREIGN KEY(aluno_id) REFERENCES alunos(id))"
    ])

def adicionar_livro(client, titulo, autor, isbn, localizacao):
    if not client: return False
    try:
        client.execute(
            "INSERT INTO livros (titulo, autor, isbn, localizacao) VALUES (?, ?, ?, ?)",
            (titulo, autor, isbn, localizacao)
        )
        return True
    except Exception as e:
        st.error(f"Erro ao cadastrar livro (ISBN pode já existir): {e}")
        return False

def buscar_livros(client, query=""):
    if not client: return pd.DataFrame()
    sql_query = "SELECT id, titulo, autor, isbn, localizacao, CASE WHEN disponivel THEN 'Sim' ELSE 'Não' END as Disponível FROM livros"
    params = ()
    if query:
        sql_query += " WHERE titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?"
        like_query = f"%{query}%"
        params = (like_query, like_query, like_query)
    result_set = client.execute(sql_query, params)
    return pd.DataFrame(result_set.rows, columns=[col for col in result_set.columns])

def adicionar_aluno(client, nome, turma):
    if not client: return
    client.execute("INSERT INTO alunos (nome, turma) VALUES (?, ?)", (nome, turma))

def listar_alunos(client):
    if not client: return []
    result = client.execute("SELECT id, nome, turma FROM alunos ORDER BY nome")
    return result.rows

def realizar_emprestimo(client, livro_id, aluno_id):
    if not client: return
    data_hoje = date.today().isoformat()
    try:
        client.batch([
            ("INSERT INTO emprestimos (livro_id, aluno_id, data_emprestimo) VALUES (?, ?, ?)", (livro_id, aluno_id, data_hoje)),
            ("UPDATE livros SET disponivel = FALSE WHERE id = ?", (livro_id,))
        ])
    except Exception as e:
        st.error(f"Erro ao realizar empréstimo: {e}")

def realizar_devolucao(client, emprestimo_id, livro_id):
    if not client: return
    data_hoje = date.today().isoformat()
    try:
        client.batch([
            ("UPDATE emprestimos SET data_devolucao = ? WHERE id = ?", (data_hoje, emprestimo_id)),
            ("UPDATE livros SET disponivel = TRUE WHERE id = ?", (livro_id,))
        ])
    except Exception as e:
        st.error(f"Erro ao realizar devolução: {e}")

def listar_emprestimos_ativos(client):
    if not client: return pd.DataFrame()
    query = """
        SELECT e.id, l.titulo, a.nome as aluno, e.data_emprestimo, l.id as livro_id
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN alunos a ON e.aluno_id = a.id
        WHERE e.data_devolucao IS NULL
        ORDER BY e.data_emprestimo
    """
    result_set = client.execute(query)
    return pd.DataFrame(result_set.rows, columns=[col for col in result_set.columns])