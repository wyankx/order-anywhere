from flask_wtf import FlaskForm
from flask_wtf.file import FileSize, FileAllowed
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class RestaurantGeneralEditForm(FlaskForm):
    title = StringField('Название ресторана', validators=[DataRequired()], render_kw={'class': 'form-control'})
    logo = FileField('Логотип ресторана', validators=[FileAllowed(['jpg', 'png'], 'Только картинки с расширением jpg, png!'), FileSize(max_size=102400, message='Файл не должен превышать по размеру 100КБ')], render_kw={'class': 'form-control'})
    submit = SubmitField('Сохранить', render_kw={'class': 'btn btn-primary'})
