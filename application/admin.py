import os.path as op
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import current_app as app
from flask_admin.contrib.fileadmin import FileAdmin
from routes import AdminHomeView
from models import db, Product
from redis import Redis
from flask_admin.contrib import rediscli


# path = op.join(op.dirname(__file__), 'templates')
admin = Admin(app, index_view=AdminHomeView(), template_mode='bootstrap3')
# admin.add_view(FileAdmin(base_path=path, name="Files"))
admin.add_view(ModelView(Product, db.session))
admin.add_view(rediscli.RedisCli(Redis()))
static_path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdmin(static_path, '/static/videos', name='Video Files'))