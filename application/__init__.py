from flask import Flask
from models import db as db, MouseData
from flask_session import Session
import redis
import json
import time
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_login import LoginManager
from models import User
import eventlet
from socketio import RedisManager

eventlet.monkey_patch()
socketio = SocketIO()
session = Session()

redis_host = 'localhost'
redis_port = 6379
redis_db = 0
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
login_manager = LoginManager()


def create_app():
    '''Flask Factory'''
    flask_app = Flask(__name__, instance_relative_config=True, template_folder='templates')
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
    CORS(flask_app)
    login_manager.init_app(flask_app)
    redis_mgr = RedisManager(redis_uri, write_only=False)
    socketio.init_app(flask_app, async_mode='threading', client_manager=redis_mgr)
    db.init_app(flask_app)
    session.init_app(flask_app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('subscribe_chat')
    def handle_subscribe_chat():
        with redis_uri.subscribe('chat_channel') as pubsub:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    emit('chat_message', data, broadcast=True)

    @socketio.on('chat_message')
    def handle_chat_message(data):
        # Push the chat message to Redis
        redis_uri.emit('chat_channel', data)

    @socketio.on('join_chat_room')
    def handle_join_chat_room(room):
        join_room(room)

    @socketio.on('leave_chat_room')
    def handle_leave_chat_room(room):
        leave_room(room)

    @socketio.on('join_draw_room', namespace='/lab/live')
    def handle_join_draw_room(room):
        join_room(room)

    @socketio.on('leave_draw_room')
    def handle_leave_draw_room(room):
        leave_room(room)

    @socketio.on('draw_data', namespace='/admin/lab')
    def handle_draw_data(data):
        # Push the draw data to Redis
        redis_uri.emit('draw_channel', data)
        # Store the pixel data in Redis
        # r.rpush('draw_channel"', data)
        # Broadcast the pixel data to all connected clients
        socketio.emit('/lab/live', data, broadcast=True)

    @socketio.on('subscribe_draw', namespace='/lab/live')
    def handle_subscribe_draw():
        with redis_uri.subscribe('draw_channel') as pubsub:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    emit('chat_message', data, broadcast=True)

    @socketio.on('submit', namespace='/admin/lab')
    def submit(data):
        movements = json.dumps(data['movements'])
        drawing = json.dumps(data['last_drawing'])
        r.set('last_drawing', drawing)
        r.set('movements', movements)
        mouse_data = MouseData(movements=movements, drawing=drawing)
        db.session.add(mouse_data)
        db.session.commit()

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


'''
        def push_data():
            while True:
                data = {'time': time.time()}
                socketio.emit('data', data, namespace='/lab/live', room='draw_channel')
                time.sleep(1)
        
        # redis_uri.start_background_task(push_data)
'''


if __name__ == '__main__':
    app = create_app()
    # eventlet run --worker-class eventlet -w 1 app:app
    socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
