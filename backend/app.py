from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Book

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/api/books", methods=["GET"])
def get_books():
    search = request.args.get("search")

    if search:
        books = Book.query.filter(
            (Book.title.ilike(f"%{search}%")) |
            (Book.author.ilike(f"%{search}%"))
        ).all()
    else:
        books = Book.query.all()

    return jsonify([
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "isbn": b.isbn,
            "status": b.status
        }
        for b in books
    ])

@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.json
    book = Book(
        title=data["title"],
        author=data["author"],
        isbn=data["isbn"]
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({"message": "Book added"}), 201

@app.route("/api/books/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.status = "borrowed"
    db.session.commit()
    return jsonify({"message": "Book borrowed"})

@app.route("/api/books/<int:book_id>/return", methods=["POST"])
def return_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.status = "available"
    db.session.commit()
    return jsonify({"message": "Book returned"})

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})

if __name__ == "__main__":
    app.run(debug=True)
