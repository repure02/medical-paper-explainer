from flask import Flask

from api.routes import api_bp
from ui.routes import ui_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(ui_bp)

if __name__ == "__main__":
    app.run(debug=True)
