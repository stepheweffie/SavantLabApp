from flask_socketio import emit, join_room, leave_room, SocketIO
from __main__ import db
from models import MouseData, r
from PIL import Image
import numpy as np
import io
import base64
import json


channel = 'drawing_data'
socketio = SocketIO()


@socketio.on('join', namespace='/lab/live')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('joined', f'{username} has joined the {room}', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('left', f'{username} has joined the {room}', room=room)


@socketio.on('mousemove', namespace='/admin/lab')
def handle_mousemove(data):
    if len(r.llen('movements')) == 0:
        r.set('movements', data)  # Save drawing data in Redis
    else:
        r.rpush('movements', data)
    emit('movements', data, broadcast=True)  # Emit drawing data to all clients


@socketio.on('draw', namespace='/admin/lab')
def handle_draw(data):
    # Store the pixel data in Redis
    r.rpush(channel, data)
    # Broadcast the pixel data to all connected clients
    socketio.emit('/lab/live', data, broadcast=True)


@socketio.on('drawing_data', namespace='/admin/lab')
def handle_drawing_data(data):
    base64_data = data['drawing_data']
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data))
    img_array = np.array(image)
    # Do something with the NumPy array, e.g., save it to a file or perform analysis

