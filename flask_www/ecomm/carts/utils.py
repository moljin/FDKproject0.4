import uuid

from flask import session
from flask_login import current_user

from flask_www.accounts.utils import login_required
from flask_www.commons.utils import elapsed_day
from flask_www.configs import db
from flask_www.ecomm.carts.models import Cart


def _cart_id():
    """session 에 cart_id를 담아두는 방법이다.
    브라우저를 닫으면 session 에 저장된 cart_id가 삭제된다.
    카트에 상품을 담은 후라면, 브라우저를 닫더라도... 카트에 담겼던 상품을 삭제하지 않으면,
    카트와 그에 저장된 상품들은 db 에 보관되어 있는 상태이다."""
    if 'cart_id' in session:
        session['cart_id'] = session.get('cart_id')
    else:
        session['cart_id'] = str(uuid.uuid4())
    return session['cart_id']


def new_cartproduct_create(new_cartproduct, product_obj, pd_single_applied_price, pd_count, pd_total_price):
    new_cartproduct.shopcategory_id = product_obj.shopcategory_id
    new_cartproduct.title = product_obj.title
    new_cartproduct.price = product_obj.price
    new_cartproduct.applied_price = pd_single_applied_price
    new_cartproduct.base_dc_amount = product_obj.base_dc_amount
    new_cartproduct.product_subtotal_quantity = int(pd_count)
    new_cartproduct.product_subtotal_price = int(pd_total_price)


def new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price):
    new_cartproductoption.option_id = op_id[idx]
    new_cartproductoption.title = option_obj.title
    new_cartproductoption.price = option_obj.price
    new_cartproductoption.op_quantity = int(op_count[idx])
    new_cartproductoption.op_line_price = int(op_total_price[idx])


def cartproduct_update(old_cartproduct, pd_count, pd_total_price):
    old_cartproduct.product_subtotal_quantity += int(pd_count)
    old_cartproduct.product_subtotal_price += int(pd_total_price)


@login_required
def cart_total_price(cart, cart_products):
    exist_total_price = 0
    for cart_product in cart_products:
        exist_total_price += cart_product.line_price
    cart.cart_total_price = exist_total_price
    current_db_sessions = db.session.object_session(cart)
    current_db_sessions.add(cart)
    db.session.commit()


def cart_active_check(cart):
    beyond_days = elapsed_day(cart.updated_at)
    print(" cart_active_check(cart): beyond_days", beyond_days)
    if beyond_days >= 1:
        cart.is_active = False
        cart.cart_id = "비구매 1개월 초과 카트"
        cart = Cart(user_id=current_user.id, cart_id=_cart_id())
        db.session.add(cart)
        db.session.commit()

