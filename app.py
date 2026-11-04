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

if __name__ == "__main__":
    app.run(debug=True)