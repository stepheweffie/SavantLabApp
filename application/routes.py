import json
import time
from flask import send_file
import os
import subprocess
from flask import current_app as app
from flask import render_template, redirect, url_for, request, session, Response, g
from __main__ import db, r
from flask_admin import expose, AdminIndexView, BaseView
from models import Recreate, Recording, MouseData
from forms import DrawingForm
from flask_admin.contrib.sqla import ModelView
import cv2
import numpy as np
import pygame
import base64
import io
from PIL import Image
from flask_socketio import emit, SocketIO, join_room
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

socketio = SocketIO(app)

""" 
the landing page will allow a client to view a menu on mobile and more on large screens
/lab is the stream first lab view 
/harmony has an optional demo and "draw like Demoness" interactive game/experience  
"""
drawing_form = DrawingForm


def is_two_factor_authenticated():
    # Replace this with the appropriate condition to check if the user is authenticated with 2FA
    return True if 'two_factor_auth' in session and session['two_factor_auth'] is True else False


@app.before_request
def load_user():
    try:
        username = session.get("username")
        if username:
            g.user = db.session.get(session["username"])
        else:
            g.user = None
    except KeyError:
        pass


@app.route('/', methods=['GET', 'POST'])
def landing_page():  # put application's code here
    if request.method == 'POST':
        session['email'] = request.form['email']
        # TODO validate and email the generated auth code
        return redirect(url_for('check_email'))
    return render_template('landingpage.html')


@app.route('/check-email', methods=['GET', 'POST'])
def check_email():
    # TODO email validation, generate, and send validation auth code
    if request.method == 'POST':
        # TODO check auth and pop the email into a mongo database
        session['auth'] = request.form['auth']
        session.pop('email', None)
        return redirect(url_for('index'))
    return render_template('check_email.html')


@app.route('/notebook')
def notebook():
    nb_path = os.path.join(os.getcwd(), 'drawing_analysis.ipynb')
    html_path = os.path.join(os.getcwd(), 'drawing_analysis.html')
    # Convert the notebook to an HTML file
    subprocess.call(['jupyter', 'nbconvert', '--to', 'html', nb_path, '--output', html_path])
    # Serve the HTML file
    return send_file(html_path)



@app.route('/lab/live')
def screen_feed():
    join_room(channel)
    drawing_data = r.lrange(channel, 0, -1)
    return render_template('live_stream.html', drawing_data=drawing_data)
def lab_live():
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            success, image = cap.read()
            if not success:
                continue
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            annotated_image = mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            ret, jpeg = cv2.imencode('.jpg', annotated_image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/lab', methods=['GET', 'POST'])
def index():  # put lab here
    form = drawing_form
    if is_two_factor_authenticated:
        return render_template('lab.html', form=form)
    if request == 'POST':
        if form.validate_on_submit():
            pixel_data = request.json['pixel_data']
            pressure_data = request.json['pressure_data']
            # Store the pixel and pressure data in Redis
            r.set('pixel_data', pixel_data)
            r.set('pressure_data', pressure_data)
            redirect(url_for('index'))
        else:
            redirect(url_for('index'))
    if 'lab' in session:
        return url_for('screen_feed')
    else:
        return redirect(url_for('landing_page'))


@app.route('/harmony')
def harmony():  # put application's code here
    if is_two_factor_authenticated:
        return redirect(url_for('index'))
    if admin_login:
        return render_template('lab.html')
    return render_template('harmony.html')


@app.route('/demoness')
def demoness():  # put application's code here
    return 'Redirect to portfolio app artist statement goes here'


@app.route('/some-encrypted-string')
def admin_login():  # put application's code here
    return 'Admin login link goes here, two factor auth'


@app.route('/articles')
def articles():  # put application's code here
    return 'Articles served from a database app'


@app.route('/recording')
def recording_feed():
    def record():
        Recording.start_recording()
        for frame in Recording.frames:
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        Recording.frames = []
    return Response(record(), mimetype='multipart/x-mixed-replace; boundary=frame',)


@app.route('/webcam')
def webcam_feed():
    def cam():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Encode the frame as jpeg
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(cam(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recreate')
def recreate_feed():
    def redraw():
        Recreate.start_recreate(self=True)
        return Response(redraw(), mimetype='multipart/x-mixed-replace; boundary=frame',
                        content_type='text/event-stream')


channel = 'drawing_data'


@socketio.on('mousemove', namespace='/admin/harmony')
def handle_mousemove(data):
    if len(r.llen('movements')) == 0:
        r.set('movements', data)  # Save drawing data in Redis
    else:
        r.rpush('movements', data)
    emit('movements', data, broadcast=True)  # Emit drawing data to all clients


@socketio.on('draw', namespace='/admin/harmony')
def handle_draw(data):
    # Store the pixel data in Redis
    r.rpush(channel, data)
    # Broadcast the pixel data to all connected clients
    socketio.emit('lab/live', data, broadcast=True)


@socketio.on('drawing_data', namespace='/admin/harmony')
def handle_drawing_data(data):
    base64_data = data['drawing_data']
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data))
    img_array = np.array(image)
    # Do something with the NumPy array, e.g., save it to a file or perform analysis


@socketio.on('submit', namespace='/admin/harmony')
    def submit(data):
        movements = json.dumps(data['movements'])
        drawing = json.dumps(data['last_drawing'])
        r.set('last_drawing', drawing)
        r.set('movements', movements)
        mouse_data = MouseData(movements=movements, drawing=drawing)
        db.session.add(mouse_data)
        db.session.commit()



class MyLab(BaseView):
    @expose('/', methods=['GET', 'POST'])
    @expose('/harmony')
    def index(self):
        form = drawing_form
        if form.validate_on_submit(self):
            return self.render('harmony.html', form=form)
        return self.render('harmony.html', form=form)


class AdminHomeView(AdminIndexView):
    @expose('/', methods=['GET'])
    @app.route('/admin')
    def admin_index(self):
        return self.render('admin/index.html', lab_links=True)


