
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ulysses_acervo.db"


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    with conectar() as conexao:
        conexao.executescript("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                categoria TEXT,
                ano INTEGER,
                quantidade INTEGER NOT NULL DEFAULT 1
                    CHECK (quantidade >= 1)
            );

            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                matricula TEXT NOT NULL UNIQUE,
                turma TEXT
            );

            CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                livro_id INTEGER NOT NULL,
                data_emprestimo TEXT NOT NULL,
                data_devolucao_prevista TEXT NOT NULL,
                data_devolucao_real TEXT,
                status TEXT NOT NULL DEFAULT 'Emprestado'
                    CHECK (
                        status IN ('Emprestado', 'Devolvido')
                    ),
                FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                FOREIGN KEY (livro_id) REFERENCES livros(id)
            );
        """)


if __name__ == "__main__":
    criar_tabelas()
    print(f"Banco de dados criado em: {DB_PATH}")