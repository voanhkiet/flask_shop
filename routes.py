from flask import render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message
from weasyprint import HTML
from datetime import datetime
import stripe
import os

from models import db, User, Product, Order, OrderItem
from app import app, mail

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS




# ------------- ROUTES -----------
@app.route("/")
def index():
  products = Product.query.all()
  return render_template("index.html", products=products)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("⚠️ Please fill in all fields.")
            return redirect(url_for("register"))

        # Check if username or email already exist
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("⚠️ Username or email already exists.")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Account created successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET","POST"])
def login():
  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
      login_user(user)
      return redirect(url_for("index"))
    flash("Invalid credentials")
  return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("index"))

# 🛒 Add item to cart
@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    for item in cart:
        if item["id"] == product.id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": 1
        })

    session["cart"] = cart
    flash(f"🛒 Added {product.name} to your cart.")
    return redirect(url_for("index"))

# Remove items from cart if the product no longer exists




# 🧾 View cart
@app.route("/cart")
@login_required
def cart():
   # 🧹 Clean invalid products from cart
    cart = session.get("cart", [])
    valid_cart = [item for item in cart if Product.query.get(item["id"])]
    session["cart"] = valid_cart

    total = sum(item["price"] * item["quantity"] for item in valid_cart)
    return render_template("cart.html", cart=valid_cart, total=total)

# ❌ Remove item from cart
@app.route("/remove_from_cart/<int:product_id>")
@login_required
def remove_from_cart(product_id):
  cart = session.get("cart", [])
  cart = [item for item in cart if item["id"] != product_id]
  session["cart"] = cart
  flash("Item removed from your cart.")
  return redirect(url_for("cart"))



@app.route("/orders")
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("orders.html", orders=orders)

@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("order_detail.html", order=order)

@app.route("/order/<int:order_id>/invoice")
@login_required
def download_invoice(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()

    # ✅ generate absolute URL for the logo
    logo_url = url_for("static", filename="favicon.ico", _external=True)

    rendered = render_template("invoice.html", order=order, logo_url=logo_url)

    pdf = HTML(string=rendered, base_url=request.root_url).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=invoice_order_{order.id}.pdf"
    return response

@app.route("/order/<int:order_id>/invoice/pdf")
@login_required
def download_invoice_pdf(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    rendered_html = render_template("invoice.html", order=order)

    # Generate PDF from HTML
    pdf = HTML(string=rendered_html, base_url=request.base_url).write_pdf()

    # Return the PDF as a response for download
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=invoice_{order.id}.pdf"

    return response

@app.route("/checkout")
@login_required
def checkout():
    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty!")
        return redirect(url_for("cart"))

    # Calculate total
    total = sum(item["price"] * item["quantity"] for item in cart)

    # Create Stripe line items
    line_items = []
    for item in cart:
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {"name": item["name"]},
                "unit_amount": int(item["price"] * 100),  # convert to cents
            },
            "quantity": item["quantity"],
        })
    
    # Create Stripe Checkout Session
    session_data = stripe.checkout.Session.create(
      payment_method_types=["card"],
      line_items=line_items,
      mode="payment",
      success_url=url_for("payment_success", _external=True),
      cancel_url=url_for("cart", _external=True),
      customer_email=f"{current_user.username}@example.com"  # optional 
    )

    return redirect(session_data.url, code=303)

@app.route("/payment_success")
@login_required
def payment_success():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    order = Order(user_id=current_user.id, total=total, is_paid=True)
    db.session.add(order)
    db.session.commit()

    for item in cart:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["id"],
            product_name=item["name"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.session.add(order_item)
    db.session.commit()

    # Clear cart early so duplicate emails don't reattach old cart
    session.pop("cart", None)

    # Render the invoice HTML (use absolute base_url so images/static assets load)
    invoice_html = render_template("invoice.html", order=order, logo_url=url_for('static', filename='favicon.ico', _external=True))
    invoice_pdf = HTML(string=invoice_html, base_url=request.root_url).write_pdf()

    # Build confirmation email
    msg = Message(
        subject=f"🧾 Your Flask Shop Order #{order.id} Confirmation",
        recipients=[current_user.email],  # adapt if you store real emails
    )
    msg.html = render_template("email_order_success.html", order=order)
    mail.send(msg)
    # Attach the invoice PDF in-memory
    msg.attach(
        filename=f"invoice_order_{order.id}.pdf",
        content_type="application/pdf",
        data=invoice_pdf
    )

    # Send the email
    mail.send(msg)

    flash("✅ Payment successful! Confirmation email (with invoice) sent.")
    return redirect(url_for("orders"))



  


@app.route("/checkout/success/<int:order_id>")
@login_required
def checkout_success(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("checkout_success.html", order=order)

@app.route("/admin/products")
@login_required
def admin_products():
    products = Product.query.all()
    return render_template("admin_products.html", products=products)


@app.route("/admin/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]

        image_file = request.files.get("image")
        image_filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)
            image_filename = f"uploads/{filename}"

        new_product = Product(
            name=name,
            price=price,
            description=description,
            image=image_filename
        )

        db.session.add(new_product)
        db.session.commit()
        flash("✅ Product added successfully with image!")
        return redirect(url_for("admin_products"))

    return render_template("add_product.html")

@app.route("/admin/orders")
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash("Access denied. Admins only.")
        return redirect(url_for("index"))

    orders = Order.query.order_by(Order.date.desc()).all()
    return render_template("admin_orders.html", orders=orders)




@app.route("/admin/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.price = float(request.form["price"])
        product.description = request.form["description"]

        # ✅ Handle image upload (optional)
        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)
            product.image = f"uploads/{filename}"  # Update with new image path

        db.session.commit()
        flash("✅ Product updated successfully!")
        return redirect(url_for("admin_products"))

    return render_template("edit_product.html", product=product)

@app.route("/admin/update_shipping/<int:order_id>", methods=["POST"])
@login_required
def update_shipping(order_id):
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for("index"))

    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    user = User.query.get(order.user_id)

    if not new_status:
        flash("No shipping status selected.")
        return redirect(url_for("admin_orders"))

    # 🚫 Avoid resending the same stage
    if order.shipping_status == new_status:
        flash(f"⚠️ Order #{order.id} is already marked as '{new_status}'. No email sent.")
        return redirect(url_for("admin_orders"))

    order.shipping_status = new_status
    timestamp = datetime.utcnow()

    # Record timeline events
    if new_status == "Processing":
        order.processing_date = timestamp
        order.shipping_stage_index = 0
    elif new_status == "Shipped":
        order.shipped_date = timestamp
        order.shipping_stage_index = 1
    elif new_status == "In Transit":
        order.in_transit_date = timestamp
        order.shipping_stage_index = 2
    elif new_status == "Delivered":
        order.delivered_date = timestamp
        order.shipping_stage_index = 3

    db.session.commit()

    # 📨 Send email notification (only once per new stage)
    msg = Message(
        subject=f"📦 Your Flask Shop Order #{order.id} is now {new_status}",
        recipients=[user.email],
    )
    msg.html = render_template("email_shipping_update.html", order=order, user=user)
    mail.send(msg)

    flash(f"🚚 Order #{order.id} updated to '{new_status}'. Email sent.")
    return redirect(url_for("admin_orders"))





@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]

        # ✅ Handle image upload (optional)
        image_file = request.files.get("image")
        image_filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)
            image_filename = f"uploads/{filename}"  # relative path for Flask `static/`

        # ✅ Create new product record
        new_product = Product(
            name=name,
            price=price,
            description=description,
            image=image_filename  # now includes image support
        )

        db.session.add(new_product)
        db.session.commit()

        flash("✅ Product added successfully with image!")
        return redirect(url_for("admin_products"))

    return render_template("add_product.html")


@app.route("/admin/delete_product/<int:product_id>")
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("🗑️ Product deleted.")
    return redirect(url_for("admin_products"))


@app.route("/clear_cart")
@login_required
def clear_cart():
    session.pop("cart", None)
    flash("🧹 Cart cleared successfully.")
    return redirect(url_for("index"))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied. Admins only.")
        return redirect(url_for("index"))

    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = sum(order.total for order in Order.query.all())

    # For chart data (e.g. revenue per order)
    orders = Order.query.order_by(Order.id.desc()).limit(10).all()
    chart_labels = [f"Order #{o.id}" for o in orders]
    chart_data = [o.total for o in orders]

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        chart_labels=chart_labels,
        chart_data=chart_data
    )

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = app.config["STRIPE_WEBHOOK_SECRET"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")

        # 🧾 Mark order as paid
        order = Order.query.filter_by(is_paid=False).order_by(Order.id.desc()).first()
        if order:
            order.is_paid = True
            db.session.commit()
            print(f"✅ Order #{order.id} marked as PAID for {customer_email}")

    return jsonify(success=True)

@app.route("/dashboard")
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date.desc()).all()
    total_spent = sum(order.total for order in orders if order.is_paid)
    total_orders = len(orders)
    delivered_orders = len([o for o in orders if o.shipping_status == "Delivered"])

    return render_template(
        "dashboard.html",
        user=current_user,
        orders=orders,
        total_spent=total_spent,
        total_orders=total_orders,
        delivered_orders=delivered_orders,
    )





@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]

        if request.form["password"]:
            current_user.password = generate_password_hash(request.form["password"])

        # Handle avatar upload
        file = request.files.get("avatar")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            current_user.avatar = filename  # Save filename to DB

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_profile.html")

@app.route("/health")
def health():
    return {"status": "ok", "message": "Flask app is running fine!"}, 200

@app.route("/ping")
def ping():
    return "pong", 200