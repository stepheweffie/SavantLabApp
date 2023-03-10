from flask import current_app as app

""" 
the landing page will allow a client to view a menu on mobile and more on large screens
/lab is the stream first lab view 
/harmony has an optional demo and "draw like Demoness" interactive game/experience  
"""


@app.route('/')
def landing_page():  # put application's code here
    return "/templates/landingpage.html"


@app.route('/lab')
def index():  # put application's code here
    return 'SavantLab goes here'


@app.route('/harmony')
def harmony():  # put application's code here
    return 'SavantLabHarmony redirect goes here'


@app.route('/harmony/demoness')
def harmony_demoness():  # put application's code here
    return 'SavantLabHarmonyWithDemoness redirect goes here'


@app.route('/archives')
def archives():  # put application's code here
    return 'SavantLabArchives playlist goes here'


@app.route('/shop')
def shop():  # put application's code here
    return 'SavantLabShop redirect goes here, external app'


@app.route('/demoness')
def demoness():  # put application's code here
    return 'Redirect to portfolio app artist statement goes here'


@app.route('/some-encrypted-string')
def admin_login():  # put application's code here
    return 'Admin login link goes here, two factor auth'


@app.route('/articles')
def articles():  # put application's code here
    return 'Articles served from a database app'
