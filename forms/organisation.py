from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class OrganisationForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()], render_kw={'class': 'form-control'})
    submit = SubmitField('Сохранить', render_kw={'class': 'btn btn-primary'})
