from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional

class AddBookForm(FlaskForm):
    title = StringField('Tên sách', validators=[DataRequired()])
    category = StringField('Thể loại', validators=[DataRequired()])
    author = StringField('Tác giả', validators=[DataRequired()])
    author_link = StringField('Link tác giả', validators=[Optional()])
    translator = StringField('Dịch giả', validators=[Optional()])
    publisher = StringField('Nhà xuất bản', validators=[Optional()])
    size = StringField('Kích thước', validators=[Optional()])
    pages = IntegerField('Số trang', validators=[Optional()])
    stock = IntegerField('Tồn kho', validators=[DataRequired()])
    release_date = StringField('Ngày phát hành', validators=[Optional()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    price = StringField('Giá', validators=[DataRequired()])
    price_old = StringField('Giá cũ', validators=[Optional()])
    discount = StringField('Giảm giá', validators=[Optional()])
    book_url = StringField('URL sách', validators=[Optional()])
    book_img = StringField('Ảnh sách', validators=[Optional()])
    submit = SubmitField('Thêm sách')

class AdminAccountForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Search')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')