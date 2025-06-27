from flask import render_template, url_for,  request, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegisterForm, PaymentForm
from models import *
from datetime import datetime


def user_routes(app, db):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route('/')
    def index():
        new_books = Book.query.filter_by(category='sach-moi-xuat-ban').limit(5).all()
        authors = Author.query.limit(6).offset(912).all()
        upcoming_books = Book.query.filter_by(category='sach-sap-xuat-ban').limit(5).all()
        print(new_books)
        print(upcoming_books)
        return render_template(
            'index.html',
            new_books=new_books,
            authors=authors,
            upcoming_books=upcoming_books
        )

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if request.method == 'POST':
            if User.query.filter_by(email=form.email.data).first():
                return render_template('register.html', form=form, error='User already exists!')
            new_user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                hashed_password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
                admin=0
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            u = User.query.filter_by(email=form.email.data).first()
            if u and check_password_hash(u.hashed_password, form.password.data):
                login_user(u, remember=form.remember.data)
                return redirect(url_for('index'))
            error = 'Email or password is incorrect!'
            return render_template('login.html', form=form, error=error)
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/book/<int:id>')
    def book(id):
        book = Book.query.get_or_404(id)
        relative_books = Book.query\
            .filter(Book.category.like(f"%{book.category}%"))\
            .filter(Book.id != book.id)\
            .limit(5).offset(10).all()
        author = Author.query.filter(Author.name.like(f"%{book.author}%")).first()
        return render_template(
            'book.html',
            book=book,
            relative_books=relative_books,
            author=author
        )

    @app.route('/author/<int:id>')
    def author(id):
        author = Author.query.get_or_404(id)
        book = Book.query.filter_by(author_link=author.author_url).first()
        if book:
            relative_books = Book.query\
                .filter(Book.category.like(f"%{book.category}%"))\
                .filter(Book.title != book.title)\
                .limit(5).all()
        else:
            relative_books = []
        return render_template(
            'author.html',
            author=author,
            book=book,
            relative_books=relative_books
        )

    @app.route('/category/<category>')
    def category(category):
        page = request.args.get('page', 1, type=int)
        per_page = 20
        pagination = Book.query.filter(Book.category.ilike(f"%{category}%")).paginate(page=page, per_page=per_page, error_out=False)
        books = pagination.items
        total_pages = pagination.pages
        return render_template(
            'category.html',
            books=books,
            category=category,
            page=page,
            total_pages=total_pages
        )

    @app.route('/cart')
    @login_required
    def cart():
        items = []
        total = 0
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        for ci in cart_items:
            price = ci.book.price
            try:
                price_int = int(price.replace('.', '').replace('₫', ''))
            except Exception:
                price_int = 0
            qty = getattr(ci, 'quantity', 1)
            line_total = price_int * qty
            total += line_total
            items.append({
                'book_img': ci.book.book_img,
                'title': ci.book.title,
                'line_total': line_total,
                'quantity': qty,
                'unit_price': price_int,
                'book_id': ci.book.id,
            })
        formatted_total = f"{total:,}".replace(',', '.') + "₫"
        return render_template(
            'cart.html',
            items=items,
            total_price=formatted_total
        )

    @app.route('/add-to-cart/<int:book_id>', methods=['POST'])
    @login_required
    def add_to_cart(book_id):
        cart_item = Cart(user_id=current_user.id, book_id=book_id)
        db.session.add(cart_item)
        db.session.commit()
        return redirect(url_for('cart'))

    @app.route('/delete-from-cart/<int:book_id>', methods=['POST'])
    @login_required
    def delete_from_cart(book_id):
        Cart.query.filter_by(user_id=current_user.id, book_id=book_id).delete()
        db.session.commit()
        return redirect(url_for('cart'))

    @app.route('/payment', methods=['GET', 'POST'])
    @login_required
    def payment():
        form = PaymentForm()
        items = []
        total = 0
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        for ci in cart_items:
            price = ci.book.price
            try:
                price_int = int(price.replace('.', '').replace('₫', ''))
            except Exception:
                price_int = 0
            qty = getattr(ci, 'quantity', 1)
            line_total = price_int * qty
            total += line_total
            items.append({
                'book_img': ci.book.book_img,
                'title': ci.book.title,
                'line_total': line_total,
                'quantity': qty,
                'unit_price': price_int,
                'book_id': ci.book.id,
            })
        formatted_total = f"{total:,}".replace(',', '.') + "₫"

        if request.method == 'POST' and form.validate_on_submit():
            order = Order(
                user_id=current_user.id,
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                address=form.address.data,
                province=form.province.data,
                district=form.district.data,
                ward=form.ward.data,
                note=form.note.data,
                shipping_method=form.shipping_method.data or 'COD',
                discount_code=form.discount_code.data,
                subtotal=total,
                shipping_fee=0,
                total=total,
                status='NEW',
                created_at=datetime.utcnow()
            )
            db.session.add(order)
            db.session.commit()

            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=item['book_id'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    line_total=item['line_total']
                )
                db.session.add(order_item)
            db.session.commit()

            Cart.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()

            return redirect(url_for('order_confirmation', order_id=order.id))

        return render_template('payment.html', items=items, form=form, total_price=formatted_total)

    @app.route('/order-confirmation/<int:order_id>')
    @login_required
    def order_confirmation(order_id):
        order = Order.query.get_or_404(order_id)
        items = []
        for oi in order.order_items:
            items.append({
                'book_img': oi.book.book_img,
                'title': oi.book.title,
                'unit_price': oi.unit_price,
                'quantity': oi.quantity,
                'line_total': oi.line_total
            })
        order_dict = {
            'id': order.id,
            'full_name': order.full_name,
            'email': order.email,
            'phone': order.phone,
            'address': order.address,
            'province': order.province,
            'district': order.district,
            'ward': order.ward,
            'note': order.note,
            'shipping_method': order.shipping_method,
            'discount_code': order.discount_code,
            'subtotal': order.subtotal,
            'shipping_fee': order.shipping_fee,
            'total': order.total,
            'created_at': order.created_at.strftime('%d/%m/%Y %H:%M')
        }
        return render_template('order_confirmation.html', order=order_dict, items=items)

    @app.route('/authors')
    def authors():
        page = request.args.get('page', 1, type=int)
        per_page = 12
        pagination = Author.query.paginate(page=page, per_page=per_page, error_out=False)
        authors = pagination.items
        total_pages = pagination.pages
        return render_template('authors.html', authors=authors, page=page, total_pages=total_pages)

    @app.route('/news')
    def news():
        return render_template('news.html')



