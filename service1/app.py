from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///./nn.db'
    app.config['SECRET_KEY'] = '041'

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    from routes import user_routes   
    user_routes(app, db)

    migrate = Migrate(app, db)

    from flask_admin.contrib.sqla import ModelView
    from models import User, Book, Author, Order, OrderItem, Cart
    admin = Admin(app, name='Admin', template_mode='bootstrap4')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Book, db.session))
    admin.add_view(ModelView(Author, db.session))
    admin.add_view(ModelView(Order, db.session))
    admin.add_view(ModelView(OrderItem, db.session))
    admin.add_view(ModelView(Cart, db.session))

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(user=current_user if current_user.is_authenticated else None)

    return app