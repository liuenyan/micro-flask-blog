# -*- coding: utf8 -*-

from .. import db, moment
from . import main
from flask import render_template, request, redirect, url_for, abort, flash, current_app
from flask.ext.login import login_required, current_user
from ..models import User, Post, Role, Permission, Category
from .forms import EditProfileForm, EditProfileAdminForm, EditPostForm
from datetime import datetime
from ..decorators import admin_required
import hashlib
import json


@main.route("/", methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int) 
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template("index.html", posts=posts, pagination=pagination)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", posts=[post])


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.WRITE_ARTICLES):
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category_id = form.categories.data
        post.timestamp = datetime.utcnow()
        db.session.add(post)
        flash(u"文章已更新")
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    if post.category is not None:
        form.categories.data = post.category.id
    return render_template('edit-post.html', form=form)


@main.route('/new-post', methods=['GET', 'POST'])
@login_required
def new_post():
    if not current_user.can(Permission.WRITE_ARTICLES):
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post(author=current_user._get_current_object(), title=form.title.data, body=form.body.data, category_id=form.categories.data)
        db.session.add(post)
        flash(u'文章已保存')
        return redirect(url_for('.index'))
    return render_template('edit-post.html', form=form)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("user.html", user=user)


@main.route("/edit-profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u"个人资料已更新")
        return redirect(url_for('.user', username=current_user.username))
    form.full_name.data = current_user.full_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit-profile.html", form=form)


@main.route("/edit-profile/<int:id>", methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.avatar_hash = hashlib.md5(form.email.data.encode('utf8')).hexdigest()
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.full_name = form.full_name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.full_name.data = user.full_name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit-profile.html', form=form, user=user)


@main.route('/user/<username>/categories', methods=['GET', 'POST'])
def categories(username):
    author = User.query.filter_by(username=username).first()
    categories = Category.query.filter_by(author=author)
    return render_template('categories.html', author=author, categories=categories)


@main.route('/user/<username>/category/<int:category_id>')
def category(username, category_id):
    page = request.args.get('page', 1, type=int) 
    pagination = Post.query.filter_by(category_id=category_id).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('category.html', posts=posts, pagination=pagination, username=username, category_id=category_id)


@main.route('/add-category', methods=['POST'])
@login_required
def add_category():
    new_category = request.form.get('new_category')
    data = {'result': 'false'}

    if new_category is not None and Category.query.filter_by(user_id=current_user.id, name=new_category).first() is None:
        category = Category(author=current_user._get_current_object(), name=new_category)
        db.session.add(category)
        db.session.commit()
        data['result'] = 'true'
        data['category_id'] = category.id
        data['category_name'] = category.name
    return json.dumps(data)

