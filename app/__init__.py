from flask import Flask

flask_app = Flask(__name__)

# import configurations from config.py
flask_app.config.from_pyfile('config.py')
flask_app.entry_point = flask_app.config['ENTRY_POINT']