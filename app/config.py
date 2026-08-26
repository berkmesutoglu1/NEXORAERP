import os
try:
    from dotenv import load_dotenv
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))
except ImportError:
    basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nexora-erp-dev-secret-key-987654'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration with SQLite fallback if MySQL is not available
    db_url = os.environ.get('DATABASE_URL')
    if not db_url or db_url == 'sqlite:///nexora_erp.db':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(basedir), 'nexora_erp.db')
    else:
        SQLALCHEMY_DATABASE_URI = db_url

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
