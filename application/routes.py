import json
import time
from flask import send_file
import os
import subprocess
from flask import current_app as app
from flask import render_template, redirect, url_for, request, session, Response
from __main__ import db, r
from flask_admin import expose, AdminIndexView, BaseView
from models import Recreate, Recording, Drawing
from forms import DrawingForm
from flask_admin.contrib.sqla import ModelView
import cv2
import pygame
# app.py
import base64
import io
from PIL import Image
from flask_socketio import emit, SocketIO, join_room
socketio = SocketIO(app)

""" 
the landing page will allow a client to view a menu on mobile and more on large screens
/lab is the stream first lab view 
/harmony has an optional demo and "draw like Demoness" interactive game/experience  
"""


@app.before_request
def load_user():
    if "auth" in session:
        g.user = db.session.get(session["username"])


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


@app.route('/lab', methods=['GET', 'POST'])
def index():  # put lab here
    if 'auth' in session:
        return render_template('lab.html')
    if 'lab' in session:
        return url_for(screen_feed)
    else:
        return redirect(url_for('landing_page'))


@app.route('/notebook')
def notebook():
    nb_path = os.path.join(os.getcwd(), 'drawing_analysis.ipynb')
    html_path = os.path.join(os.getcwd(), 'drawing_analysis.html')

    # Convert the notebook to an HTML file
    subprocess.call(['jupyter', 'nbconvert', '--to', 'html', nb_path, '--output', html_path])

    # Serve the HTML file
    return send_file(html_path)


@app.route('/lab/live', methods=['GET'])
def screen_feed():
    join_room(channel)
    pixel_data = r.lrange(channel, 0, -1)
    return render_template('live_stream.html', pixel_data=pixel_data)


@app.route('/harmony')
def harmony():  # put application's code here
    return render_template('harmony.html')


@app.route('/harmony-lab')
def harmony_lab():
    def submit_drawing():
        form = DrawingForm()
        if form.validate_on_submit():
            # Get the drawing data from the form
            drawing_data = request.form.get('drawing_data')

            # Save the drawing data to the SQLite database
            new_drawing = Drawing(data=drawing_data)
            db.session.add(new_drawing)
            db.session.commit()

            return redirect(url_for('success'))
        return render_template('harmony_lab.html', form=form)
    return render_template('harmony_lab.html')


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
    return Response(record(), mimetype='multipart/x-mixed-replace; boundary=frame',
                    )


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


channel = 'pixel_data'


# app.py
@socketio.on('mousemove')
def handle_mousemove(data):
    r.set('drawing_data', data)  # Save drawing data in Redis
    emit('drawing_data', data, broadcast=True)  # Emit drawing data to all clients


@socketio.on('draw')
def handle_draw(data):
    # Store the pixel data in Redis
    r.rpush(channel, data)
    # Broadcast the pixel data to all connected clients
    socketio.emit('lab/live', data, broadcast=True)


@socketio.on('drawing_data')
def handle_drawing_data(data):
    base64_data = data['pixel_data']
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data))
    img_array = np.array(image)
    # Do something with the NumPy array, e.g., save it to a file or perform analysis


class MyLab(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if request == 'POST':
            pixel_data = request.json['pixel_data']
            pressure_data = request.json['pressure_data']
            # Store the pixel and pressure data in Redis
            r.set('pixel_data', pixel_data)
            r.set('pressure_data', pressure_data)
            return self.render('harmony_lab.html')
        return self.render('harmony_lab.html')


class AdminHomeView(AdminIndexView):
    @expose('/', methods=['GET'])
    @app.route('/admin')
    def admin_index(self):
        return self.render('admin/index.html', lab_links=True)


