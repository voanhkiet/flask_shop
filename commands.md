# 🧭 Flask Shop Quick Notes

## App Startup

flask run

## Common Flask Imports

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

## Database Shell

flask shell

> > > from app import db, Product
> > > Product.query.all()

## Routes

/ -> index.html
/register -> register.html
/login -> login.html
/cart -> cart.html
/admin/products -> admin_products.html
/admin/dashboard -> admin_dashboard.html
