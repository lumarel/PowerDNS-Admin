import os
import logging
import re
from flask import Flask
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_migrate import Migrate
from flask_session import Session
from cachelib.file import FileSystemCache
from .lib import utils
from .models import db

def create_app(config=None):
    from powerdnsadmin.lib.settings import AppSettings
    from . import models, routes, services
    from .assets import assets
    app = Flask(__name__)

    # Read log level from environment variable
    log_level_name = os.environ.get('PDNS_ADMIN_LOG_LEVEL', 'WARNING')
    log_level = logging.getLevelName(log_level_name.upper())
    # Setting logger
    logging.basicConfig(
       level=log_level,
        format=
        "[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s")

    # If we use Docker + Gunicorn, adjust the
    # log handler
    if "GUNICORN_LOGLEVEL" in os.environ:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # Proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Load config from env variables if using docker
    if os.path.exists(os.path.join(app.root_path, 'docker_config.py')):
        app.config.from_object('powerdnsadmin.docker_config')
    else:
        # Load default configuration
        app.config.from_object('powerdnsadmin.default_config')

    # Load config file from FLASK_CONF env variable
    if 'FLASK_CONF' in os.environ:
        app.config.from_envvar('FLASK_CONF')

    # Load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    # Load any settings defined with environment variables
    AppSettings.load_environment(app)

    #Initialize db only once 
    db.init_app(app)
    _migrate = Migrate(app, db)  # lgtm [py/unused-local-variable]

    # Read version from VERSION file
    version_file_path = os.path.join(app.root_path, '..', 'VERSION')
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as version_file:
            version = version_file.read().strip()
            # Validate the version format using a regular expression
            if re.match(r'^\d+\.\d+\.\d+(-\w+(\.\w+)*)?(\+\w+(\.\w+)*)?$', version):
                app.config['VERSION'] = version
            else:
                raise ValueError(f"Invalid version format: {version}")


    # HSTS
    if app.config.get('HSTS_ENABLED'):
        from flask_sslify import SSLify
        _sslify = SSLify(app)  # lgtm [py/unused-local-variable]

    # Load Flask-Session
    app.config['SESSION_TYPE'] = app.config.get('SESSION_TYPE','sqlalchemy')
    if 'SESSION_TYPE' in os.environ:
        app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE')

    # Initialize session with existing SQLAlchemy instance
    if app.config['SESSION_TYPE'] == 'sqlalchemy':
        app.config['SESSION_SQLALCHEMY'] = db

    if app.config['SESSION_TYPE'] == 'cachelib':
        app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
    sess = Session(app)

    # SMTP
    app.mail = Mail(app)

    # Load app's components
    assets.init_app(app)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)

    # Register filters
    app.jinja_env.filters['display_record_name'] = utils.display_record_name
    app.jinja_env.filters['display_master_name'] = utils.display_master_name
    app.jinja_env.filters['display_second_to_time'] = utils.display_time
    app.jinja_env.filters['display_setting_state'] = utils.display_setting_state
    app.jinja_env.filters['pretty_domain_name'] = utils.pretty_domain_name
    app.jinja_env.filters['format_datetime_local'] = utils.format_datetime
    app.jinja_env.filters['format_zone_type'] = utils.format_zone_type

    # Register context processors
    from .models.setting import Setting

    @app.context_processor
    def inject_sitename():
        setting = Setting().get('site_name')
        return dict(SITE_NAME=setting)

    @app.context_processor
    def inject_setting():
        setting = Setting()
        return dict(SETTING=setting)

    @app.context_processor
    def inject_version():
        return dict(version=app.config['VERSION'])

    return app
