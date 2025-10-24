import os
import sys

# ✅ Ensure project directory is in sys.path early
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from models import db  # ✅ Now Flask will find this correctly

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask app
app = Flask(
    __name__,
    template_folder="templates",
    static_folder= "static"
)
app.config.from_object(Config)

# ✅ Initialize extensions
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))

# ✅ Import routes after app setup
with app.app_context():
    print(">>> Loading routes.py ...") # Add this
    import routes
    print(">>> Routes successfully imported!") # Addd this

if __name__ == "__main__":
    app.run(debug=True, port=5001)
