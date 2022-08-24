from flask import Blueprint, render_template

NAME = 'commons'
common_bp = Blueprint(NAME, __name__)


@common_bp.route('/')
def index():
    return render_template('index.html')
