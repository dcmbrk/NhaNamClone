from flask import render_template, url_for, request, redirect, abort, request
from werkzeug.security import  check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, AddBookForm
from models import *


def admin_routes(app, db):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/books', methods=['GET', 'POST'])
    @login_required
    def books():
        books_per_page = 12
        page = request.args.get('page', 1, type=int)
        query = Book.query
        pagination = query.paginate(page=page, per_page=books_per_page, error_out=False)
        books = pagination.items
        total_pages = pagination.pages

        pages_range = []
        if total_pages > 1:
            pages_range.append(1)
            if page - 3 > 1:
                pages_range.append('...')
            for p in range(page - 2, page + 3):
                if 1 < p < total_pages:
                    pages_range.append(p)
            if page + 2 < total_pages - 1:
                pages_range.append('...')
            if total_pages != 1:
                pages_range.append(total_pages)

        return render_template(
            'books.html',
            books=books,
            page=page,
            total_pages=total_pages,
            pages_range=pages_range
        )
    
    @app.route('/books/add', methods=['GET', 'POST'])
    @login_required
    def add_book():
        form = AddBookForm()
        if request.method == 'POST' and form.validate_on_submit():
            try: 
                new_book = Book(
                    title=form.title.data,
                    category=form.category.data,
                    author=form.author.data,
                    author_link=form.author_link.data,
                    translator=form.translator.data,
                    publisher=form.publisher.data,
                    size=form.size.data,
                    pages=form.pages.data,
                    stock=form.stock.data,
                    release_date=form.release_date.data,
                    description=form.description.data,
                    price=form.price.data,
                    price_old=form.price_old.data,
                    discount=form.discount.data,
                    book_img=form.book_img.data,
                    book_url=form.book_url.data
                )
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(f"Error adding book: {e}")
                return "Có lỗi khi thêm sách."
            return redirect(url_for('books'))
        return render_template('add_book.html', form=form)

    from forms import AdminAccountForm  

    def admin_required(f):
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.admin:
                abort(403)
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function

    @app.route('/admin/accounts')
    @app.route('/accounts')
    @login_required
    @admin_required
    def accounts():
        accounts = User.query.all()
        form = AdminAccountForm()  
        return render_template('accounts.html', accounts=accounts, form=form)

    @app.route('/admin/accounts/add/<int:account_id>', methods=['POST'])
    @login_required
    @admin_required
    def update_account(account_id):
        account = User.query.get(account_id)
        if account:
            account.admin = 0 if account.admin == 1 else 1
            db.session.commit()
        accounts = User.query.all()
        form = AdminAccountForm() 
        return render_template('accounts.html', accounts=accounts, form=form)

    @app.route('/admin/login', methods=['GET', 'POST'])
    @app.route('/', methods=['GET', 'POST'])
    def admin_login():
        error = None
        form = LoginForm()
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            admin = User.query.filter_by(email=email, admin=1).first()
            if admin and check_password_hash(admin.hashed_password, password):
                login_user(admin)
                return redirect(url_for('accounts'))  
            error = 'Invalid email or password. Please try again.'
        return render_template('admin_login.html', error=error, form=form)

    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        return render_template('admin_dashboard.html')

    @app.route('/admin/orders')
    @login_required
    @admin_required
    def admin_orders():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items
        total_pages = pagination.pages
        return render_template('admin_orders.html', orders=orders, page=page, total_pages=total_pages)

    @app.route('/admin/orders/<int:order_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_order_detail(order_id):
        order = Order.query.get_or_404(order_id)
        if request.method == 'POST':
            order.status = request.form.get('status')
            db.session.commit()
            return redirect(url_for('admin_order_detail', order_id=order.id))
        return render_template('admin_order_detail.html', order=order)

    @app.route('/admin/books')
    @login_required
    @admin_required
    def admin_books():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
        books = pagination.items
        total_pages = pagination.pages
        return render_template('admin_books.html', books=books, page=page, total_pages=total_pages)

    @app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_edit_book(book_id):
        book = Book.query.get_or_404(book_id)
        form = AddBookForm(obj=book)
        if request.method == 'POST' and form.validate_on_submit():
            book.title = form.title.data
            book.category = form.category.data
            book.author = form.author.data
            book.author_link = form.author_link.data
            book.translator = form.translator.data
            book.publisher = form.publisher.data
            book.size = form.size.data
            book.pages = form.pages.data
            book.stock = form.stock.data
            book.release_date = form.release_date.data
            book.description = form.description.data
            book.price = form.price.data
            book.price_old = form.price_old.data
            book.discount = form.discount.data
            book.book_img = form.book_img.data
            book.book_url = form.book_url.data
            db.session.commit()
            return redirect(url_for('admin_books'))
        return render_template('admin_edit_book.html', form=form, book=book)

    @app.route('/admin/logout')
    @login_required
    @admin_required
    def admin_logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/news')
    def news():
        return render_template('news.html')

    @app.route('/books/delete/<int:book_id>', methods=['POST'])
    @login_required
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('books'))


