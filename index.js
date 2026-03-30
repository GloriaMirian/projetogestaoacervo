import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function BibliotecaApp() {
  const [books, setBooks] = useState([
    { id: 1, title: "Dom Casmurro", author: "Machado de Assis", borrowed: false },
    { id: 2, title: "1984", author: "George Orwell", borrowed: true },
  ]);

  const [search, setSearch] = useState("");
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [editingId, setEditingId] = useState(null);

  const filteredBooks = books.filter(
    (book) =>
      book.title.toLowerCase().includes(search.toLowerCase()) ||
      book.author.toLowerCase().includes(search.toLowerCase())
  );

  const handleAddOrEdit = () => {
    if (!title || !author) return;

    if (editingId) {
      setBooks((prev) =>
        prev.map((b) =>
          b.id === editingId ? { ...b, title, author } : b
        )
      );
      setEditingId(null);
    } else {
      setBooks((prev) => [
        ...prev,
        { id: Date.now(), title, author, borrowed: false },
      ]);
    }

    setTitle("");
    setAuthor("");
  };

  const handleDelete = (id) => {
    setBooks((prev) => prev.filter((b) => b.id !== id));
  };

  const handleEdit = (book) => {
    setTitle(book.title);
    setAuthor(book.author);
    setEditingId(book.id);
  };

  const toggleBorrow = (id) => {
    setBooks((prev) =>
      prev.map((b) =>
        b.id === id ? { ...b, borrowed: !b.borrowed } : b
      )
    );
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Sistema de Biblioteca</h1>

      {/* Formulário */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-6">
        <Input
          placeholder="Título"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Input
          placeholder="Autor"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
        />
        <Button onClick={handleAddOrEdit}>
          {editingId ? "Salvar" : "Adicionar"}
        </Button>
      </div>

      {/* Busca */}
      <Input
        placeholder="Buscar livro..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-6"
      />

      {/* Lista */}
      <div className="grid gap-4">
        {filteredBooks.map((book) => (
          <Card key={book.id}>
            <CardContent className="p-4 flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold">{book.title}</h2>
                <p className="text-sm text-gray-500">{book.author}</p>
                <p className={`text-xs ${book.borrowed ? "text-red-500" : "text-green-600"}`}>
                  {book.borrowed ? "Emprestado" : "Disponível"}
                </p>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => toggleBorrow(book.id)}>
                  {book.borrowed ? "Devolver" : "Emprestar"}
                </Button>
                <Button variant="outline" onClick={() => handleEdit(book)}>
                  Editar
                </Button>
                <Button variant="destructive" onClick={() => handleDelete(book.id)}>
                  Excluir
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
