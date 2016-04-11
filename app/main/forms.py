# -*- coding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, Required
from flask.ext.pagedown.fields import PageDownField
class EditProfileForm(Form):
    full_name = StringField(u'姓名', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')


class EditPostForm(Form):
    title = StringField(u'标题', validators=[Length(0, 64)])
    #body = TextAreaField(u'内容')
    body = PageDownField(u'使用MarkDown编辑内容', validators=[Required()])
    submit = SubmitField(u'提交')
