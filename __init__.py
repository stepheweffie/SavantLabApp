from flask import Flask


def create_app():
    '''Flask Factory'''
    flask_app = Flask(__name__, instance_relative_config=True)
    print('Uses .env and config.py for settings ')
    from werkzeug.utils import import_string
    cfg = import_string('config.DevConfig')()
    flask_app.config.from_object(cfg)
    with flask_app.app_context():
        # From application module
        from application import routes
        print("Flask Factory Built")
        return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
