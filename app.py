from flask import Flask
from flask_cors import CORS
from routes.health import health_bp
from routes.routes_api import routes_bp

def create_app():
    app = Flask(__name__)
    CORS(app)   # ← CORS eklendi

    app.register_blueprint(health_bp)
    app.register_blueprint(routes_bp)

    @app.route("/")
    def home():
        return "Logictics backend çalışıyor!"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
