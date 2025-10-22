from flask import Flask
from models import db
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os
import sys
sys.paht.append(os.path.dirname(__file__))

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

# ✅ Move this import *below* everything else
# and import inside a context to avoid circular import
def register_routes():
    import routes

register_routes()

# ✅ For local runs only (not used by Render)
if __name__ == "__main__":
    app.run(debug=True)
