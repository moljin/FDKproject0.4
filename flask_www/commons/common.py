from flask import Blueprint, render_template
from flask_login import current_user

from flask_www.commons.utils import elapsed_day
from flask_www.ecomm.carts.models import Cart

NAME = 'commons'
common_bp = Blueprint(NAME, __name__)


@common_bp.route('/')
def index():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        if cart:
            return render_template('index.html', cart=cart)
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')
