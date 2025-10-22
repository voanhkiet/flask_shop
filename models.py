from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy() # Create db object here(no import from app)

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  email = db.Column(db.String(150), unique=True, nullable=False)
  password = db.Column(db.String(200), nullable=False)
  is_admin = db.Column(db.Boolean, default=False) # ✅ new field
  avatar = db.Column(db.String(200), default='default.png') # 🆕 avatar image filename

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  price = db.Column(db.Float, nullable=False)
  description = db.Column(db.String(200))
  image = db.Column(db.String(200), nullable=True)

class Order(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  date = db.Column(db.DateTime, default=datetime.utcnow)
  total = db.Column(db.Float, nullable=False)
  is_paid = db.Column(db.Boolean, default=False)

  # 🆕 Multiple shipping stages
  shipping_status = db.Column(db.String(50), default="Processing") # current stage
  shipping_stage_index = db.Column(db.Integer, default=0) # track progress

  # 🆕 Track all stages (optinal for analytics)
  processing_date = db.Column(db.DateTime, nullable=True)
  shipped_date = db.Column(db.DateTime, nullable=True)
  in_transit_date = db.Column(db.DateTime, nullable=True)
  delivered_date = db.Column(db.DateTime, nullable=True)


  order_items = db.relationship("OrderItem", backref="order", lazy=True)

  def __repr__(self):
        return f"<Order {self.id} - Paid: {self.is_paid}>"
  
class OrderItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=True)
  product_name = db.Column(db.String(100), nullable=False)   # ✅ add this line
  quantity = db.Column(db.Integer, nullable=False)
  price = db.Column(db.Float, nullable=False)

  product = db.relationship("Product", backref="order_items")


# Run create_all inside app context
if __name__ == "__main__":
  with app.app_context():
    db.create_all()
    print("✅ Database and tables created successfully!")
