from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
admin = Admin()


def create_app():
    '''Flask Factory'''
    flask_app = Flask(__name__, instance_relative_config=True)
    print('Uses .env and config.py for settings ')
    from werkzeug.utils import import_string
    cfg = import_string('config.DevConfig')()
    flask_app.config.from_object(cfg)
    flask_app.config['SECRET_KEY'] = 'mysecretkey'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
    db.init_app(flask_app)
    with flask_app.app_context():
        # From application module
        import routes
        import forms
        import models
        admin.init_app(flask_app)
        print("Flask Factory Built")
        db.create_all()
        print("Store Database Built")
        return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
