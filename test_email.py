from app import mail, Message, app
from models import Order, User

with app.app_context():
    order = Order.query.first()
    user = User.query.get(order.user_id)

    msg = Message(
        subject=f"📦 Your Flask Shop Order #{order.id} is now {order.shipping_status}",
        recipients=["voanhkiet261192@gmail.com"]
    )
    msg.html = f"""
    <h3>Hi {user.username},</h3>
    <p>Your order <b>#{order.id}</b> has been updated to:
       <b style='color:blue'>{order.shipping_status}</b>.</p>
    <p>Order total: ${order.total}</p>
    <p>Thank you for shopping with Flask Shop!</p>
    """
    mail.send(msg)
    print("📧 Test shipping email sent!")
