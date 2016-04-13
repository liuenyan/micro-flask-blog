# -*- encoding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo

class LoginForm(Form):
    email = StringField(u'邮件地址', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')

class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    new_password = PasswordField(u'新密码', validators=[Required(), EqualTo('new_password', message=u'两次密码输入必须一致')])
    new_password2 = PasswordField(u'新密码', validators=[Required()])
    submit = SubmitField(u'更新密码')
