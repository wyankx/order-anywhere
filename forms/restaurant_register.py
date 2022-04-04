from flask_wtf import FlaskForm
from flask_wtf.file import FileSize, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired


class RestaurantRegisterForm(FlaskForm):
    title = StringField('Название ресторана', validators=[DataRequired()], render_kw={'class': 'form-control'})
    logo = FileField('Логотип ресторана', validators=[FileAllowed(['jpg', 'png'], 'Только картинки с расширением jpg, png!'), FileSize(max_size=1024000, message='Файл не должен превышать по размеру 100КБ')], render_kw={'class': 'form-control'})
    login = StringField('Логин', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    redirect_after_send_order = StringField('Куда направлять клиента после отправки заказа', render_kw={'class': 'form-control'})
    submit = SubmitField('Зарегистрироваться', render_kw={'class': 'btn btn-primary'})
