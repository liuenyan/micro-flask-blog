from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime
import hashlib
from flask import request, current_app
from markdown import markdown
import bleach

class Permission:
   FOLLOW = 0x01
   COMMENT = 0x02
   WRITE_ARTICLES = 0x04
   MODERATE_COMMENT = 0x08
   ADMINISTRATOR = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENT, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, default=roles[r][1], permissions=roles[r][0])
                db.session.add(role)
            db.session.commit()
 
    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    full_name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf8')).hexdigest()
    
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions == permissions)
    
    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)
 
    def ping(self):
        self.last_login = datetime.utcnow()
        db.session.add(self)

    def change_email(self, new_email):
        pass

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username
    
    @staticmethod
    def generate_fake(count=10):
        from random import seed
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        seed()
        for i in range(count):
            u = User(username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(), 
                    email=forgery_py.internet.email_address(),
                    full_name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

 
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def user_load(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    def __repr__(self):
        return "<Post %r>" % self.id

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        user_count = User.query.count()
        seed()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post(title=forgery_py.lorem_ipsum.word(), 
                    body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                    timestamp=datetime.utcnow(),
                    author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_body_changed(target, value, oldvalue, initiator):
        allowed_tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_body_changed)

