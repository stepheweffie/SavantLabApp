import os.path as op
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import current_app as app
from flask_admin.contrib.fileadmin import FileAdmin
from routes import AdminHomeView, MyLab
from models import db, Drawing
from redis import Redis
from flask_admin.contrib import rediscli


class RecordingAdminView(ModelView):
    column_list = ('id', 'datetime', 'recording_array')  # list of columns to display in the view
    can_create = False  # allow users to create new records
    can_edit = False  # allow users to edit existing records
    can_delete = False  # allow users to delete records
    page_size = 50  # number of records to display per page


# TODO make articles_path a mongo db view
lab_path = op.join(op.dirname(__file__), 'labs')
# articles_path = op.join(op.dirname(__file__), 'articles')
admin = Admin(app, index_view=AdminHomeView(), template_mode='bootstrap3')
admin.add_view(FileAdmin(base_path=lab_path, name="Labs"))
# admin.add_view(FileAdmin(base_path=articles_path, name='Articles'))
admin.add_view(RecordingAdminView(Drawing, db.session))
admin.add_view(rediscli.RedisCli(Redis()))