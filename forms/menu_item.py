from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired

from flask_login import current_user


class MenuItemForm(FlaskForm):
    item_image = FileField('Фото', validators=[FileAllowed(['jpg', 'png'], 'Только картинки с расширением jpg, png!')], render_kw={'class': 'form-control'})
    title = StringField('Название', validators=[DataRequired()], render_kw={'class': 'form-control'})
    price = IntegerField('Цена', validators=[DataRequired()], render_kw={'class': 'form-control'})
    category = SelectField('Категория', validators=[DataRequired()], choices=lambda: [category.title for category in current_user.menu.categories], render_kw={'class': 'form-select'})
    submit = SubmitField('Сохранить', render_kw={'class': 'btn btn-primary'})
