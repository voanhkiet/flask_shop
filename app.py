import os
import sys

# ✅ Ensure Render can always import local modules (like routes.py)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from flask import Flask
from models import db
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))

# ✅ Import routes safely
def register_routes():
    try:
        import routes  # first try (works locally)
        print("✅ Imported routes successfully.")
    except ModuleNotFoundError as e:
        print("⚠️ Could not import routes:", e)
        print("🔧 Current working directory:", os.getcwd())
        print("🔧 Python sys.path:", sys.path)

register_routes()

if __name__ == "__main__":
    app.run(debug=True)
