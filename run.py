# This is only for development.

from app.routes import app as app
app.debug=True
app.run(port=8080, host='0.0.0.0')
