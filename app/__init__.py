from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.secret_key ="REST SECRET"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://project:project@localhost:8080/epicmealplan'

from app import views
