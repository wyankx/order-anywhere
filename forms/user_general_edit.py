from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UserGeneralEditForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()], render_kw={'class': 'form-control'})
    surname = StringField('Фамилия', validators=[DataRequired()], render_kw={'class': 'form-control'})
    submit = SubmitField('Сохранить', render_kw={'class': 'btn btn-primary'})
