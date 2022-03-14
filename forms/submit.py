from flask_wtf import FlaskForm
from wtforms import SubmitField


class SubmitForm(FlaskForm):
    submit = SubmitField('Подтвердить', render_kw={'class': 'btn btn-primary'})
