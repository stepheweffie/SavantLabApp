from flask import current_app as app


@app.route('/')
def landing_page():  # put application's code here
    return 'SavantLabLandingPage goes here'


@app.route('/index')
def index():  # put application's code here
    return 'SavantLabIndex goes here'


@app.route('/harmony')
def harmony():  # put application's code here
    return 'SavantLabHarmony goes here'


@app.route('/live')
def live():  # put application's code here
    return 'SavantLabLive goes here'


@app.route('/archives')
def archives():  # put application's code here
    return 'SavantLabArchives goes here!'


@app.route('/shop')
def shop():  # put application's code here
    return 'SavantLabShop goes here'



