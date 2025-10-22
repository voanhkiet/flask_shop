import os
import sys
sys.path.append(os.path.dirname(__file__))  # ✅ fixed line

from flask import Flask
from models import db
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
import os
import sys
sys.path.append(os.path.dirname(__file__))  # ✅ ensures local imports work everywhere

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

# ✅ Import routes after app is created
def register_routes():
    import routes  # routes.py is in the same directory as app.py

register_routes()

if __name__ == "__main__":
    app.run(debug=True)

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
    import routes

register_routes()

if __name__ == "__main__":
    app.run(debug=True)
