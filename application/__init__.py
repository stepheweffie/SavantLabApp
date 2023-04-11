from flask import Flask
from models import db as db
from flask_session import Session
import redis
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager
from models import User
from socketio_events import socketio
import eventlet

eventlet.monkey_patch()

session = Session()

redis_host = 'localhost'
redis_port = 6379
redis_db = 0
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
login_manager = LoginManager()


def create_app():
    '''Flask Factory'''
    flask_app = Flask(__name__, instance_relative_config=True)
    print('Uses .env and config.py for settings ')
    from werkzeug.utils import import_string
    cfg = import_string('config.DevConfig')()
    flask_app.config.from_object(cfg)

    flask_app.config['SECRET_KEY'] = 'mysecretkey'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab.db'
    flask_app.config['SESSION_TYPE'] = 'redis'
    flask_app.config['REDIS_URI'] = 'redis://localhost:6379/0'
    redis_uri = flask_app.config['REDIS_URI']
    flask_app.config['SESSION_REDIS'] = redis.from_url(redis_uri)
    flask_app.config['REDIS_URL'] = redis_uri
    CORS(flask_app)
    login_manager.init_app(flask_app)
    socketio.init_app(flask_app)
    db.init_app(flask_app)
    session.init_app(flask_app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with flask_app.app_context():
        # From application module
        import routes
        import forms
        import models
        import admin
        import socketio_events
        db.create_all()
        print("Flask Factory Built")
        print("Store Database Built")
        return flask_app


if __name__ == '__main__':
    app = create_app()
    # eventlet run --worker-class eventlet -w 1 app:app
    socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
