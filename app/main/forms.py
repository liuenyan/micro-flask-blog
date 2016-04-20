# -*- coding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import Length, Required, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Category
from flask.ext.login import current_user

class EditProfileForm(Form):
    full_name = StringField(u'姓名', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')


class EditProfileAdminForm(Form):
    email = StringField(u'邮件地址', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只能包含字母、数字、"_"、和"."')])
    role = SelectField(u'用户角色', coerce=int)
    full_name = StringField(u'姓名', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class EditPostForm(Form):
    title = StringField(u'标题', validators=[Length(0, 64)])
    #body = TextAreaField(u'内容')
    body = PageDownField(u'使用MarkDown编辑内容', validators=[Required()])
    categories = SelectField(u'分类', coerce=int)
    submit = SubmitField(u'提交')

    def __init__(self):
        super(EditPostForm, self).__init__()
        if current_user.is_authenticated:
            self.categories.choices = [(category.id, category.name) for category in Category.query.filter_by(author=current_user._get_current_object()).order_by(Category.name).all()]
