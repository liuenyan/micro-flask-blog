import os
from flask.ext.bootstrap import WebCDN, BOOTSTRAP_VERSION, JQUERY_VERSION
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or\
            'hard to guess string'
    FLASKY_POSTS_PER_PAGE = 10
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
            os.path.join(basedir, 'mcrio_fask_blog_db.sqlite')
    #BOOTSTRAP_SERVE_LOCAL = True
    @staticmethod
    def init_app(app):
        app.extensions['bootstrap']['cdns']['bootstrap'] = WebCDN('//cdn.bootcss.com/bootstrap/%s/' % BOOTSTRAP_VERSION)
        app.extensions['bootstrap']['cdns']['jquery'] = WebCDN('//cdn.bootcss.com/jquery/%s/' % JQUERY_VERSION)

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}
