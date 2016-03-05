from . import main
from flask import render_template
from flask.ext.login import login_required

@main.route("/")
@login_required
def index():
    return render_template("index.html")
