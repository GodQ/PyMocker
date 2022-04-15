from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_cors

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data.db'
db = SQLAlchemy(app)
flask_cors.CORS(app=app)

db.create_all()