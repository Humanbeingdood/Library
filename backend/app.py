from flask import Flask, request, jsonify, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_cors import CORS
from models import db, Book, User

app = Flask(__name__, static_folder="frontend")
app.secret_key = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
CORS(app, supports_credentials=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin", password="password")
        db.session.add(user)
        db.session.commit()

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
        isbn=data["isbn"],
        image=data.get("image")
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({"message": "Book added"}), 201
 
@app.route("/")
def dashboard():
    return send_from_directory("frontend", "dashboard.html")

@app.route("/catalog")
def catalog():
    return send_from_directory("frontend", "index.html")

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

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()

    if user and user.password == data["password"]:
        login_user(user)
        return jsonify({"message": "Logged in"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@app.route("/api/me")
def me():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username})
    return jsonify({"username": None})

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json

    # Check if username already exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(
        username=data["username"],
        password=data["password"]  # plain text for learning
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

if __name__ == "__main__":
    app.run(debug=True)
