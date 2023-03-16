from flask import current_app as app
from flask import render_template, redirect, url_for, request, session
from __main__ import db
from flask_admin import expose, AdminIndexView
from forms import ProductForm
from models import Product


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
def index():  # put application's code here
    if 'auth' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('landing_page'))


@app.route('/harmony')
def harmony():  # put application's code here
    return render_template('harmony.html')


@app.route('/harmony/demoness')
def harmony_demoness():  # put application's code here
    return redirect(url_for('archives'))


@app.route('/archives')
def archives():  # put application's code here
    return 'SavantLabArchives playlist goes here'


@app.route('/shop')
def shop():  # put application's code here
    return render_template('products.html')


@app.route('/cart')
def cart():  # put application's code here
    return render_template('cart.html')


@app.route('/demoness')
def demoness():  # put application's code here
    return 'Redirect to portfolio app artist statement goes here'


@app.route('/some-encrypted-string')
def admin_login():  # put application's code here
    return 'Admin login link goes here, two factor auth'


@app.route('/articles')
def articles():  # put application's code here
    return 'Articles served from a database app'


class AdminHomeView(AdminIndexView):
    @expose('/', methods=['GET'])
    @app.route('/admin')
    def admin_index(self):
        form = ProductForm()
        if request.method == 'GET':
            return self.render('/admin/index.html', form=form)
        if form.validate_on_submit():
            product = Product(name=form.name.data, description=form.description.data)
            db.session.add(product)
            db.session.commit()
            form.name.data = ''
            form.description.data = ''
        return render_template('index.html', form=form)