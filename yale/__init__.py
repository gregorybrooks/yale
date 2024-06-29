from datetime import datetime
import os
import logging

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
#    logging.basicConfig(level=logging.INFO,
#                        filename=app.instance_path + r'/webapp.log',
#                        format='%(asctime)s - %(message)s',
#                        datefmt='%Y-%m-%d %H:%M:%S')

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='landing_page')

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Starting PubMed search. Press Ctrl+C to exit.")

    return app
