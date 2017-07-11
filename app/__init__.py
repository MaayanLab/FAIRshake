from flask import Flask

ENTRY_POINT = '/MyApp/'

flask_app = Flask(__name__, static_url_path=ENTRY_POINT + 'static', static_folder='static')

# import configurations from config.py
flask_app.config.from_pyfile('config.py')
flask_app.entry_point = ENTRY_POINT

# Setup routes after initializing Flask app
import routes
