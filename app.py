from database import criar_tabelas, conectar
from pathlib import Path
from flask import Flask, send_from_directory, request, jsonify

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=None)


@app.route("/")
def inicio():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/js/<path:filename>")
def arquivos_javascript(filename):
    return send_from_directory(BASE_DIR / "js", filename)


@app.route("/<path:filename>")
def paginas(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route("/api/livros", methods=["GET"])
def listar_livros():
    with conectar() as conexao:
        livros = conexao.execute(
            "SELECT * FROM livros ORDER BY titulo"
        ).fetchall()

    return [
        dict(livro) for livro in livros
    ]


@app.route("/api/livros", methods=["POST"])
def cadastrar_livro():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do livro em JSON."}), 400

    titulo = dados.get("titulo")
    autor = dados.get("autor")
    categoria = dados.get("categoria")
    ano = dados.get("ano")
    quantidade = dados.get("quantidade", 1)

    if not isinstance(titulo, str) or not titulo.strip():
        return jsonify({"erro": "O título é obrigatório."}), 400

    if not isinstance(autor, str) or not autor.strip():
        return jsonify({"erro": "O autor é obrigatório."}), 400

    try:
        quantidade = int(quantidade)
        if quantidade < 1:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"erro": "A quantidade deve ser um inteiro maior que zero."}), 400

    try:
        if ano in (None, ""):
            ano = None
        else:
            ano = int(ano)
            if ano < 0 or ano > 9999:
                raise ValueError
    except (TypeError, ValueError):
        return jsonify({"erro": "Informe um ano válido."}), 400

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO livros (titulo, autor, categoria, ano, quantidade)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                titulo.strip(),
                autor.strip(),
                categoria.strip() if isinstance(categoria, str) else None,
                ano,
                quantidade,
            ),
        )
        livro_id = cursor.lastrowid

        livro = conexao.execute(
            "SELECT * FROM livros WHERE id = ?", (livro_id,)
        ).fetchone()

    return jsonify(dict(livro)), 201

    
@app.route("/api/livros/<int:livro_id>", methods=["PUT"])
def atualizar_livro(livro_id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do livro em JSON."}), 400

    titulo = dados.get("titulo")
    autor = dados.get("autor")
    categoria = dados.get("categoria")
    ano = dados.get("ano")
    quantidade = dados.get("quantidade")

    if not isinstance(titulo, str) or not titulo.strip():
        return jsonify({"erro": "O título é obrigatório."}), 400

    if not isinstance(autor, str) or not autor.strip():
        return jsonify({"erro": "O autor é obrigatório."}), 400

    try:
        quantidade = int(quantidade)
        if quantidade < 1:
            raise ValueError

        ano = None if ano in (None, "") else int(ano)
        if ano is not None and not 0 <= ano <= 9999:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"erro": "Confira o ano e a quantidade."}), 400

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE livros
            SET titulo = ?, autor = ?, categoria = ?, ano = ?, quantidade = ?
            WHERE id = ?
            """,
            (
                titulo.strip(),
                autor.strip(),
                categoria.strip() if isinstance(categoria, str) else None,
                ano,
                quantidade,
                livro_id,
            ),
        )

        if cursor.rowcount == 0:
            return jsonify({"erro": "Livro não encontrado."}), 404

        livro = conexao.execute(
            "SELECT * FROM livros WHERE id = ?", (livro_id,)
        ).fetchone()

    return jsonify(dict(livro))


@app.route("/api/livros/<int:livro_id>", methods=["DELETE"])
def excluir_livro(livro_id):
    try:
        with conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM livros WHERE id = ?", (livro_id,)
            )

            if cursor.rowcount == 0:
                return jsonify({"erro": "Livro não encontrado."}), 404

    except Exception as erro:
        from sqlite3 import IntegrityError

        if isinstance(erro, IntegrityError):
            return jsonify({
                "erro": "Este livro possui empréstimos registrados e não pode ser excluído."
            }), 409
        raise

    return jsonify({"mensagem": "Livro excluído com sucesso."})

criar_tabelas()

# ==========================================
# ROTAS DE ALUNOS
# ==========================================

@app.route("/api/alunos", methods=["GET"])
def listar_alunos():
    with conectar() as conexao:
        alunos = conexao.execute(
            "SELECT * FROM alunos ORDER BY nome"
        ).fetchall()

    return jsonify([dict(aluno) for aluno in alunos])


@app.route("/api/alunos", methods=["POST"])
def cadastrar_aluno():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados em JSON."}), 400

    nome = dados.get("nome")
    matricula = dados.get("matricula")
    turma = dados.get("turma")

    if not all(
        isinstance(campo, str) and campo.strip()
        for campo in (nome, matricula, turma)
    ):
        return jsonify({
            "erro": "Preencha nome, matrícula e turma."
        }), 400

    try:
        with conectar() as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO alunos (nome, matricula, turma)
                VALUES (?, ?, ?)
                """,
                (nome.strip(), matricula.strip(), turma.strip())
            )

            aluno = conexao.execute(
                "SELECT * FROM alunos WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()

        return jsonify(dict(aluno)), 201

    except Exception as erro:
        from sqlite3 import IntegrityError

        if isinstance(erro, IntegrityError):
            return jsonify({
                "erro": "Esta matrícula já está cadastrada."
            }), 409
        raise


@app.route("/api/alunos/<int:aluno_id>", methods=["PUT"])
def atualizar_aluno(aluno_id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados em JSON."}), 400

    nome = dados.get("nome")
    matricula = dados.get("matricula")
    turma = dados.get("turma")

    if not all(
        isinstance(campo, str) and campo.strip()
        for campo in (nome, matricula, turma)
    ):
        return jsonify({
            "erro": "Preencha nome, matrícula e turma."
        }), 400

    try:
        with conectar() as conexao:
            cursor = conexao.execute(
                """
                UPDATE alunos
                SET nome = ?, matricula = ?, turma = ?
                WHERE id = ?
                """,
                (nome.strip(), matricula.strip(), turma.strip(), aluno_id)
            )

            if cursor.rowcount == 0:
                return jsonify({"erro": "Aluno não encontrado."}), 404

            aluno = conexao.execute(
                "SELECT * FROM alunos WHERE id = ?",
                (aluno_id,)
            ).fetchone()

        return jsonify(dict(aluno))

    except Exception as erro:
        from sqlite3 import IntegrityError

        if isinstance(erro, IntegrityError):
            return jsonify({
                "erro": "Esta matrícula já está cadastrada."
            }), 409
        raise


@app.route("/api/alunos/<int:aluno_id>", methods=["DELETE"])
def excluir_aluno(aluno_id):
    try:
        with conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM alunos WHERE id = ?",
                (aluno_id,)
            )

            if cursor.rowcount == 0:
                return jsonify({"erro": "Aluno não encontrado."}), 404

        return jsonify({
            "mensagem": "Aluno excluído com sucesso."
        })

    except Exception as erro:
        from sqlite3 import IntegrityError

        if isinstance(erro, IntegrityError):
            return jsonify({
                "erro": "Este aluno possui empréstimos registrados e não pode ser excluído."
            }), 409
        raise

# =========================
# ROTAS DE EMPRÉSTIMOS
# =========================

@app.route("/api/emprestimos", methods=["GET"])
def listar_emprestimos():
    with conectar() as conexao:
        emprestimos = conexao.execute("""
            SELECT
                e.id,
                e.aluno_id,
                e.livro_id,
                a.nome AS aluno,
                a.matricula,
                l.titulo AS livro,
                l.autor,
                e.data_emprestimo,
                e.data_devolucao_prevista,
                e.data_devolucao_real,
                e.status
            FROM emprestimos e
            JOIN alunos a ON a.id = e.aluno_id
            JOIN livros l ON l.id = e.livro_id
            ORDER BY e.id DESC
        """).fetchall()

    return jsonify([dict(item) for item in emprestimos])


@app.route("/api/emprestimos", methods=["POST"])
def cadastrar_emprestimo():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados em JSON."}), 400

    try:
        aluno_id = int(dados.get("aluno_id"))
        livro_id = int(dados.get("livro_id"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Selecione um aluno e um livro válidos."}), 400

    data_emprestimo = dados.get("data_emprestimo")
    data_devolucao = dados.get("data_devolucao_prevista")

    if not data_emprestimo or not data_devolucao:
        return jsonify({"erro": "Preencha as datas do empréstimo e da devolução."}), 400

    if data_devolucao < data_emprestimo:
        return jsonify({"erro": "A data de devolução não pode ser anterior ao empréstimo."}), 400

    with conectar() as conexao:
        aluno = conexao.execute(
            "SELECT id FROM alunos WHERE id = ?",
            (aluno_id,)
        ).fetchone()

        livro = conexao.execute(
            "SELECT quantidade FROM livros WHERE id = ?",
            (livro_id,)
        ).fetchone()

        if not aluno:
            return jsonify({"erro": "Aluno não encontrado."}), 404

        if not livro:
            return jsonify({"erro": "Livro não encontrado."}), 404

        emprestimos_ativos = conexao.execute("""
            SELECT COUNT(*) AS total
            FROM emprestimos
            WHERE livro_id = ? AND status = 'Emprestado'
        """, (livro_id,)).fetchone()["total"]

        disponiveis = livro["quantidade"] - emprestimos_ativos

        if disponiveis <= 0:
            return jsonify({"erro": "Não há exemplares disponíveis deste livro."}), 409

        cursor = conexao.execute("""
            INSERT INTO emprestimos (
                aluno_id,
                livro_id,
                data_emprestimo,
                data_devolucao_prevista
            )
            VALUES (?, ?, ?, ?)
        """, (
            aluno_id,
            livro_id,
            data_emprestimo,
            data_devolucao
        ))

        emprestimo = conexao.execute("""
            SELECT
                e.id,
                e.aluno_id,
                e.livro_id,
                a.nome AS aluno,
                l.titulo AS livro,
                e.data_emprestimo,
                e.data_devolucao_prevista,
                e.status
            FROM emprestimos e
            JOIN alunos a ON a.id = e.aluno_id
            JOIN livros l ON l.id = e.livro_id
            WHERE e.id = ?
        """, (cursor.lastrowid,)).fetchone()

    return jsonify(dict(emprestimo)), 201


@app.route("/api/emprestimos/<int:emprestimo_id>/devolucao", methods=["PUT"])
def registrar_devolucao(emprestimo_id):
    with conectar() as conexao:
        emprestimo = conexao.execute(
            "SELECT status FROM emprestimos WHERE id = ?",
            (emprestimo_id,)
        ).fetchone()

        if not emprestimo:
            return jsonify({"erro": "Empréstimo não encontrado."}), 404

        if emprestimo["status"] == "Devolvido":
            return jsonify({"erro": "Este empréstimo já foi devolvido."}), 409

        conexao.execute("""
            UPDATE emprestimos
            SET
                status = 'Devolvido',
                data_devolucao_real = date('now', 'localtime')
            WHERE id = ?
        """, (emprestimo_id,))

    return jsonify({
        "mensagem": "Devolução registrada com sucesso."
    })
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)