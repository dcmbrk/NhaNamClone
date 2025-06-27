from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class RegisterForm(FlaskForm):
    first_name = StringField('Họ', validators=[DataRequired()])
    last_name = StringField('Tên', validators=[DataRequired()])
    phone_number = StringField('Số điện thoại', validators=[DataRequired(), Length(min=8, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Đăng ký')

class PaymentForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Họ và tên', validators=[DataRequired()])
    phone = StringField('Số điện thoại')
    address = StringField('Địa chỉ')
    province = StringField('Tỉnh thành', validators=[DataRequired()])
    district = StringField('Quận huyện')
    ward = StringField('Phường xã')
    note = StringField('Ghi chú')
    shipping_method = StringField('Phương thức vận chuyển', default='COD')
    discount_code = StringField('Mã giảm giá')
    submit = SubmitField('ĐẶT HÀNG')


