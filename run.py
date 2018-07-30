# This is only for development.

from app.app import app as app
app.run(port=8080, host='0.0.0.0', debug=True)
