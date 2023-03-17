import os.path as op
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import current_app as app
from flask_admin.contrib.fileadmin import FileAdmin
from routes import AdminHomeView, MyLab
from models import db, Recording
from redis import Redis
from flask_admin.contrib import rediscli


class RecordingAdminView(ModelView):
    column_list = ('id', 'datetime', 'recording_array')  # list of columns to display in the view
    can_create = False  # allow users to create new records
    can_edit = False  # allow users to edit existing records
    can_delete = False  # allow users to delete records
    page_size = 50  # number of records to display per page


path = op.join(op.dirname(__file__), 'labs')
admin = Admin(app, index_view=AdminHomeView(), template_mode='bootstrap3')
admin.add_view(MyLab(name='My Lab', endpoint='harmony_lab'))
admin.add_view(FileAdmin(base_path=path, name="Labs"))
admin.add_view(RecordingAdminView(Recording, db.session))
admin.add_view(rediscli.RedisCli(Redis()))