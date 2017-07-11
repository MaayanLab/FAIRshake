from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)
CORS(app)

# Rename this.
ENTRY_POINT = '/MyApp/'

# And this.
SERVER_ROOT = os.path.dirname(os.getcwd()) + '/MyApp/app'


@app.route(ENTRY_POINT, methods=['GET'])
def index():
    return 'hello world'


@app.route(ENTRY_POINT + '<path:path>')
def send_css(path):
    print path
    return flask.send_from_directory(SERVER_ROOT, path)
