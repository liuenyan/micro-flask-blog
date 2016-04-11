# -*- coding: utf8 -*-

from .. import db, moment
from . import main
from flask import render_template, request, redirect, url_for, abort, flash, current_app
from flask.ext.login import login_required, current_user
from ..models import User, Post
from .forms import EditProfileForm, EditPostForm
from datetime import datetime


@main.route("/", methods=['GET', 'POST'])
#@login_required
def index():
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post(author=current_user._get_current_object(), title=form.title.data, body=form.body.data)
        db.session.add(post)
        flash(u'文章已保存')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int) 
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template("index.html", form=form, posts=posts, pagination=pagination)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", posts=[post])


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.timestamp = datetime.utcnow()
        db.session.add(post)
        flash(u"文章已更新")
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
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

