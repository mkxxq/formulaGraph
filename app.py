# -*- coding: utf-8 -*-
import sympy.core
from flask import Flask, render_template, request, flash, Markup, jsonify

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, TextField,\
    FormField, SelectField, FieldList
from wtforms.validators import DataRequired, Length
from wtforms.fields import *

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sympy.parsing.latex import parse_latex
from sympy.plotting import plot,plot_implicit
import matplotlib
matplotlib.use("TKAgg")

app = Flask(__name__)
app.secret_key = 'dev'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

# set default button sytle and size, will be overwritten by macro parameters
app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'
# app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'lumen'  # uncomment this line to test bootswatch theme

# set default icon title of table actions
app.config['BOOTSTRAP_TABLE_VIEW_TITLE'] = 'Read'
app.config['BOOTSTRAP_TABLE_EDIT_TITLE'] = 'Update'
app.config['BOOTSTRAP_TABLE_DELETE_TITLE'] = 'Remove'
app.config['BOOTSTRAP_TABLE_NEW_TITLE'] = 'Create'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class LatexForm(FlaskForm):
    inputVal = StringField('Latex',validators=[DataRequired(),Length(1,100)])
    submit = SubmitField()


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    draft = db.Column(db.Boolean, default=False, nullable=False)
    create_time = db.Column(db.Integer, nullable=False, unique=True)


@app.before_first_request
def before_first_request_func():
    db.drop_all()
    db.create_all()
    for i in range(20):
        m = Message(
            text=f'Test message {i+1}',
            author=f'Author {i+1}',
            category=f'Category {i+1}',
            create_time=4321*(i+1)
            )
        if i % 4:
            m.draft = True
        db.session.add(m)
    db.session.commit()


@app.route('/',methods=['GET','POST'])
def index():
    latexForm = LatexForm()
    formulaLatex = latexForm.inputVal.data
    formula = None
    if formulaLatex:
        try:
            formula = parse_latex(formulaLatex)
        except:
            formula = None
    img = ''
    p = None
    if formula is not None:
        if isinstance(formula,sympy.Equality):
            p = plot_implicit(formula,show=False)
        else:
            p = plot(formula,show=False)
        if p is not None:
            p.save("static/a.jpg")
            img = 'static/a.jpg'
    return render_template('graph.html',latex_form=latexForm,img=img)


if __name__ == '__main__':
    app.run(debug=True)
