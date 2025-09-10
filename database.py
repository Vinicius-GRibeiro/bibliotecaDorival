import streamlit as st
import libsql_client
import pandas as pd
from datetime import date


def get_connection():
    try:
        url = st.secrets["turso"]["db_url"]

        if url.startswith("https://"):
            url = url.replace("https://", "libsql://", 1)

        client = libsql_client.create_client_sync(
            url=url,
            auth_token=st.secrets["turso"]["auth_token"]
        )
        return client
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None


def init_db():
    client = get_connection()
    if client:
        client.batch([
            """
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY,
                titulo TEXT NOT NULL,
                autor TEXT,
                isbn TEXT UNIQUE,
                localizacao TEXT NOT NULL,
                disponivel BOOLEAN DEFAULT TRUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                turma TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY,
                livro_id INTEGER,
                aluno_id INTEGER,
                data_emprestimo DATE,
                data_devolucao DATE,
                FOREIGN KEY(livro_id) REFERENCES livros(id),
                FOREIGN KEY(aluno_id) REFERENCES alunos(id)
            )
            """
        ])
        client.close()


def adicionar_livro(titulo, autor, isbn, localizacao):
    client = get_connection()
    if client:
        try:
            client.execute(
                "INSERT INTO livros (titulo, autor, isbn, localizacao) VALUES (?, ?, ?, ?)",
                (titulo, autor, isbn, localizacao)
            )
            client.close()
            return True
        except Exception as e:
            st.error(f"Erro ao cadastrar livro (ISBN pode já existir): {e}")
            client.close()
            return False


def buscar_livros(query=""):
    client = get_connection()
    if not client:
        return pd.DataFrame()

    sql_query = "SELECT id, titulo, autor, isbn, localizacao, CASE WHEN disponivel THEN 'Sim' ELSE 'Não' END as Disponível FROM livros"
    params = ()

    if query:
        sql_query += " WHERE titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?"
        like_query = f"%{query}%"
        params = (like_query, like_query, like_query)

    result_set = client.execute(sql_query, params)

    df = pd.DataFrame(result_set.rows, columns=[col for col in result_set.columns])
    client.close()
    return df


def adicionar_aluno(nome, turma):
    client = get_connection()
    if client:
        client.execute("INSERT INTO alunos (nome, turma) VALUES (?, ?)", (nome, turma))
        client.close()


def listar_alunos():
    client = get_connection()
    if client:
        result = client.execute("SELECT id, nome, turma FROM alunos ORDER BY nome")
        rows = result.rows
        client.close()
        return rows
    return []


def realizar_emprestimo(livro_id, aluno_id):
    client = get_connection()
    if client:
        data_hoje = date.today().isoformat()

        try:
            client.batch([
                ("INSERT INTO emprestimos (livro_id, aluno_id, data_emprestimo) VALUES (?, ?, ?)",
                 (livro_id, aluno_id, data_hoje)),
                ("UPDATE livros SET disponivel = FALSE WHERE id = ?", (livro_id,))
            ])
            client.close()
        except Exception as e:
            st.error(f"Erro ao realizar empréstimo: {e}")
            client.close()


def realizar_devolucao(emprestimo_id, livro_id):
    client = get_connection()
    if client:
        data_hoje = date.today().isoformat()

        try:
            client.batch([
                ("UPDATE emprestimos SET data_devolucao = ? WHERE id = ?", (data_hoje, emprestimo_id)),
                ("UPDATE livros SET disponivel = TRUE WHERE id = ?", (livro_id,))
            ])
            client.close()
        except Exception as e:
            st.error(f"Erro ao realizar devolução: {e}")
            client.close()


def listar_emprestimos_ativos():
    client = get_connection()
    if not client:
        return pd.DataFrame()

    query = """
        SELECT e.id, l.titulo, a.nome as aluno, e.data_emprestimo, l.id as livro_id
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN alunos a ON e.aluno_id = a.id
        WHERE e.data_devolucao IS NULL
        ORDER BY e.data_emprestimo
    """
    result_set = client.execute(query)
    df = pd.DataFrame(result_set.rows, columns=[col for col in result_set.columns])
    client.close()
    return df