import os
from app import app
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/fyyur_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
