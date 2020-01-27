import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random
from sqlalchemy import Column, String, Integer, create_engine
import json

# ------------------Models---------------------------


database_path = 'postgresql://ajitesh@localhost:5432/bookshelf'

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

'''
Movie

'''
class Book(db.Model):
  __tablename__ = 'books'

  id = Column(Integer, primary_key=True)
  title = Column(String)
  author = Column(String)
  rating = Column(Integer)

  def __init__(self, title, author, rating):
    self.title = title
    self.author = author
    self.rating = rating

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      'author': self.author,
      'rating': self.rating,
    }

# ----------------------------------------------
BOOKS_PER_SHELF = 4

def paginate_books(request, selection):
    page = request.args.get('page', 1, type = int)
    start = (page-1)*BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books
# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/')
  def hello():
      return jsonify({'message': 'Hello World!'}),200

  @app.route('/books')
  def retrieve_books():
    selection = Book.query.order_by(Book.id).all()
    current_books = paginate_books(request, selection)

    if len(current_books) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'books': current_books,
        'total_books': len(Book.query.all())
    })

  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_book(book_id):
    body = request.get_json()

    try:
        book = Book.query.filter(Book.id==book_id).one_or_none()
        if book is None:
            abort(404)

        if 'rating' in body:
            book.rating = int(body.get('rating'))

        book.update()

        return jsonify({
        'success': True,
        'id': book_id
        })
    except:
        abort(400)

  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
      try:
          book = Book.query.filter(Book.id == book_id).one_or_none()

          if book is None:
              abort(404)

          book.delete()
          selection = Book.query.order_by(Book.id).all()
          current_books = paginate_books(request, selection)

          return jsonify({
            'success': True,
            'deleted': book_id,
            'books': current_books,
            'total_books': len(Book.query.all())
          })
      except:
          abort(422)

  @app.route('/books', methods=['POST'])
  def create_book():
      body = request.get_json()

      new_title = body.get('title', None)
      new_author = body.get('author', None)
      new_rating = body.get('rating', None)
      search = body.get('search', None)

      try:
          if search:
              selection = Book.query.order_by(Book.id).filter(Book.title.ilike("%{}%".format(search)))
              current_books = paginate_books(request, selection)

              return jsonify({
                'success': True,
                'books': current_books,
                'total_books': len(selection.all())
              })
          else:
              book = Book(
                title = new_title,
                author = new_author,
                rating = new_rating
              )

              db.session.add(book)
              db.session.commit()

              selection = Book.query.order_by(Book.id).all()
              current_books = paginate_books(request, selection)

              return ({
                'success': True,
                'created': book.id,
                'books': current_books,
                'total_books': len(Book.query.all())
              })
      except:
          abort(404)

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': "Not found"
      }), 404

  @app.errorhandler(400)
  def not_found(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad request"
      }), 400

  @app.errorhandler(422)
  def not_found(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': "Unprocessable"
      }), 422

  @app.errorhandler(405)
  def not_found(error):
      return jsonify({
        'success': False,
        'error': 405,
        'message': "Method now allowed"
      }), 405

  return app
