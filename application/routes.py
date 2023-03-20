from flask import current_app as app
from flask import render_template, redirect, url_for, request, session, Response
from __main__ import db, r
from flask_admin import expose, AdminIndexView, BaseView
from models import Recreate, Recording
from flask_admin.contrib.sqla import ModelView
import cv2
import pygame

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
        return screen_feed()
    else:
        return redirect(url_for('landing_page'))


@app.route('/lab/live', methods=['GET'])
def screen_feed():
    return render_template('live_stream.html')


@app.route('/harmony')
def harmony():  # put application's code here
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
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        Recording.stop_recording()
            Recording.record_frame()
            if not Recording.__init__().recording:
                break
        for frame in Recording.frames:
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        Recording.frames = []
    return Response(record(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/webcam')
def webcam_feed():
    def gen():
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
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recreate')
def recreate_feed():
    def redraw():
        Recreate.start_recreate(self=True)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        Recreate.stop_recreate(self=False)
            Recreate.record_frame()
            if not Recreate.__init__(self=False).recording:
                break
        for frame in Recreate.frames:
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        Recreate.frames = []
    return Response(redraw(), mimetype='multipart/x-mixed-replace; boundary=frame')


class MyLab(BaseView):
    @expose('/')
    def index(self):
        eye_data = webcam_feed()
        drawing_data = recreate_feed()
        pixel_data = recording_feed()
        return self.render('harmony_lab.html', pixel_stream=pixel_data, drawing_stream=drawing_data, eye_stream=eye_data)


class AdminHomeView(AdminIndexView):
    @expose('/', methods=['GET'])
    @app.route('/admin')
    def admin_index(self):
        return self.render('admin/index.html', lab_links=True)


