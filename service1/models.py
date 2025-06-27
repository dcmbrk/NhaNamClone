from app import db 
from datetime import datetime
from flask_login import UserMixin

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    category = db.Column(db.Text)
    author = db.Column(db.Text)
    author_link = db.Column(db.Text)
    price = db.Column(db.Text)
    price_old = db.Column(db.Text)
    discount = db.Column(db.Text)
    translator = db.Column(db.Text)
    publisher = db.Column(db.Text)
    size = db.Column(db.Text)
    pages = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    description = db.Column(db.Text)
    book_img = db.Column(db.Text)
    book_url = db.Column(db.Text)
    release_date = db.Column(db.Text)

    order_items = db.relationship('OrderItem', back_populates='book')

    def __repr__(self):
        return f"<Book id={self.id} title={self.title!r}>"

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    biography = db.Column(db.Text)
    author_img = db.Column(db.Text)
    author_url = db.Column(db.Text, unique=True)

    def __repr__(self):
        return f"<Author id={self.id} name={self.name!r}>"

class User(UserMixin, db.Model):  
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.Text)
    first_name = db.Column(db.Text)
    phone_number = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    hashed_password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Integer)

    orders = db.relationship('Order', back_populates='user')
    cart_items = db.relationship('Cart', back_populates='user')

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    user = db.relationship('User', back_populates='cart_items')
    book = db.relationship('Book')

    def __repr__(self):
        return f"<Cart id={self.id} user_id={self.user_id} book_id={self.book_id}>"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.Text, nullable=False)
    full_name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text)
    address = db.Column(db.Text)
    province = db.Column(db.Text)
    district = db.Column(db.Text)
    ward = db.Column(db.Text)
    note = db.Column(db.Text)
    shipping_method = db.Column(db.Text)
    discount_code = db.Column(db.Text)
    subtotal = db.Column(db.Integer, nullable=False)
    shipping_fee = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Text, default='NEW')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order')

    def __repr__(self):
        return f"<Order id={self.id} total={self.total}>"

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    book = db.relationship('Book', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem id={self.id} order_id={self.order_id} book_id={self.book_id}>"
    