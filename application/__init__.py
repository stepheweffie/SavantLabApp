from flask import Flask
from models import Product
from models import db as db


def create_app():
    '''Flask Factory'''
    flask_app = Flask(__name__, instance_relative_config=True)
    print('Uses .env and config.py for settings ')
    from werkzeug.utils import import_string
    cfg = import_string('config.DevConfig')()
    flask_app.config.from_object(cfg)
    flask_app.config['SECRET_KEY'] = 'mysecretkey'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
    flask_app.config['REDIS_URL'] = 'redis://localhost:6379/0'
    db.init_app(flask_app)
    with flask_app.app_context():
        # From application module
        import routes
        import forms
        import models
        import admin
        db.create_all()
        print("Flask Factory Built")
        print("Store Database Built")
        return flask_app


if __name__ == '__main__':
    app = create_app()

    app.run(host='0.0.0.0', port=5000, debug=True)
