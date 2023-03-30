from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class DrawingForm(FlaskForm):
    submit = SubmitField('Submit Drawing')
    csrf_token = HiddenField()




