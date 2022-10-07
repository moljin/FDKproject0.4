import uuid

from flask import Blueprint, request, make_response, jsonify, session, redirect, render_template, url_for, abort
from flask_login import current_user

from flask_www.accounts.utils import login_required
from flask_www.commons.models import VarRatio
from flask_www.configs import db
from flask_www.configs.config import NOW
from flask_www.ecomm.carts.models import Cart, CartProduct, CartProductOption
from flask_www.ecomm.carts.utils import new_cartproduct_create, new_cartproductoption_create, cartproduct_update, cart_total_price, _cart_id, cart_active_check  # , cart_active_check
from flask_www.ecomm.products.models import ProductOption, Product
from flask_www.ecomm.promotions.forms import AddCouponForm
from flask_www.ecomm.promotions.models import Coupon, UsedCoupon, Point, PointLog
from flask_www.ecomm.promotions.utils import cart_point_log_create, point_log_update

NAME = 'carts'
carts_bp = Blueprint(NAME, __name__, url_prefix='/carts')


@carts_bp.route('/add/to/cart/<int:_id>', methods=['POST'])
@login_required
def add_to_cart(_id):
    if request.method == 'POST':
        product_obj = Product.query.get_or_404(_id)
        option_objs = ProductOption.query.filter_by(product_id=_id).all()

        pd_count = request.form.get("pd-count")
        pd_single_applied_price = request.form.get("pd-applied-price")
        pd_total_price = request.form.get("pd-total-price")

        op_id = request.form.getlist("op-id")
        op_count = request.form.getlist("op-count")
        op_total_price = request.form.getlist("op-total-price")

        total_price = request.form.get("total-price")
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not cart:
            cart = Cart(user_id=current_user.id, cart_id=_cart_id())
            db.session.add(cart)
            db.session.commit()
        else:  # 여기로 지나갈 수는 없지만...d/t 상품페이지로 진입시 이 과정을 거친다.
            cart_active_check(cart)

        old_cartproduct = CartProduct.query.filter_by(cart_id=cart.id, product_id=_id).first()
        old_cartproductoptions = CartProductOption.query.filter_by(cart_id=cart.id, product_id=_id).all()

        if option_objs and not old_cartproduct and not old_cartproductoptions:
            new_cartproduct= CartProduct(cart_id=cart.id, product_id=_id)
            new_cartproduct_create(new_cartproduct, product_obj, pd_single_applied_price, pd_count, pd_total_price)
            db.session.add(new_cartproduct)

            if op_id:
                for idx in range(len(op_id)):
                    option_obj = ProductOption.query.get_or_404(op_id[idx])
                    new_cartproductoption = CartProductOption(cart_id=cart.id, product_id=_id)
                    new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price)
                    db.session.bulk_save_objects([new_cartproductoption])

                    new_cartproduct.op_subtotal_price += int(op_total_price[idx])
                    new_cartproduct.line_price = new_cartproduct.product_subtotal_price + new_cartproduct.op_subtotal_price
                    db.session.add(new_cartproduct)
            else:
                new_cartproduct.line_price = new_cartproduct.product_subtotal_price
                db.session.add(new_cartproduct)
            db.session.commit()

        elif option_objs and old_cartproduct and not old_cartproductoptions:
            cartproduct_update(old_cartproduct, pd_count, pd_total_price)
            db.session.add(old_cartproduct)

            for idx in range(len(op_id)):
                option_obj = ProductOption.query.get_or_404(op_id[idx])
                new_cartproductoption = CartProductOption(cart_id=cart.id, product_id=_id)
                new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price)
                db.session.bulk_save_objects([new_cartproductoption])

                old_cartproduct.op_subtotal_price += int(op_total_price[idx])
                old_cartproduct.line_price = old_cartproduct.product_subtotal_price + old_cartproduct.op_subtotal_price
                db.session.add(old_cartproduct)
            db.session.commit()

        elif option_objs and old_cartproduct and old_cartproductoptions:
            cartproduct_update(old_cartproduct, pd_count, pd_total_price)
            db.session.add(old_cartproduct)
            if op_id:
                for idx in range(len(op_id)):
                    old_cartproductoption = CartProductOption.query.filter_by(option_id=op_id[idx]).first()
                    if old_cartproductoption:
                        old_cartproductoption.op_quantity += int(op_count[idx])
                        old_cartproductoption.op_line_price += int(op_total_price[idx])
                        db.session.bulk_save_objects([old_cartproductoption])

                        old_cartproduct.op_subtotal_price += int(op_total_price[idx])
                        old_cartproduct.line_price = old_cartproduct.product_subtotal_price + old_cartproduct.op_subtotal_price
                        db.session.add(old_cartproduct)
                    else:
                        option_obj = ProductOption.query.get_or_404(op_id[idx])
                        new_cartproductoption = CartProductOption(cart_id=cart.id, product_id=_id)
                        new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price)
                        db.session.bulk_save_objects([new_cartproductoption])

                        old_cartproduct.op_subtotal_price += int(op_total_price[idx])
                        old_cartproduct.line_price = old_cartproduct.product_subtotal_price + old_cartproduct.op_subtotal_price
                        db.session.add(old_cartproduct)
            else:
                old_cartproduct.line_price = old_cartproduct.product_subtotal_price + old_cartproduct.op_subtotal_price
                db.session.add(old_cartproduct)
            db.session.commit()

        elif not option_objs and not old_cartproduct:
            new_cartproduct = CartProduct(cart_id=cart.id, product_id=_id)
            new_cartproduct_create(new_cartproduct, product_obj, pd_single_applied_price, pd_count, pd_total_price)

            new_cartproduct.line_price = new_cartproduct.product_subtotal_price
            db.session.add(new_cartproduct)
            db.session.commit()

        elif not option_objs and old_cartproduct:
            cartproduct_update(old_cartproduct, pd_count, pd_total_price)

            old_cartproduct.line_price = old_cartproduct.product_subtotal_price
            db.session.add(old_cartproduct)
            db.session.commit()

        return redirect(url_for('carts.cart_view'))


coupons = ""
used_coupons = ""


@carts_bp.route('/view', methods=['GET'])
@login_required
def cart_view():
    global coupons, used_coupons
    try:
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        # 여기에도 1개월 지난 카트를 체크해야 하나???
        # 여기로 지나갈 수는 없지만...d/t 상품페이지로 진입시 이 과정을 거친다.
        # 혹시라도 로그인하고 카트뷰 페이지로 어떻게든 들어가면...
        if cart:
            cart_active_check(cart)
            coupons = Coupon.query.filter_by(is_active=True).filter(Coupon.use_from <= NOW, Coupon.use_to >= NOW).all()
            used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()

    except Exception as e:
        print(e, 'cart_view Exception: 카트가 없고, 사용가능한 쿠폰, 사용한 쿠폰도 없다.')
        cart = None
        coupons = None
        used_coupons = None
    if current_user.is_authenticated:
        if cart and cart.is_active is True:
            add_coupon_form = AddCouponForm()
            cart_products = CartProduct.query.filter_by(cart_id=cart.id).all()
            cart_productoptions = CartProductOption.query.filter_by(cart_id=cart.id).all()

            cart_total_price(cart, cart_products)

            point_obj = Point.query.filter_by(user_id=current_user.id).first()
            point_log_obj = cart_point_log_create(cart)
            # 이때 point_obj 가 없으면, point_obj 와 point_log_obj 를 만들고,
            # point_obj 가 있으면, point_log_obj 유무를 체크하고 생성하거나 있는 것을 반환한다.

            context = {
                "cart_id": cart.id,
                'cart': cart,
                'cart_products': cart_products,
                'cart_productoptions': cart_productoptions,
                'items_total_count': len(cart_products),
                'cart_total_price': cart.cart_total_price,

                'coupons': coupons,
                'used_coupons': used_coupons,
                'add_coupon_form': add_coupon_form,

                'point_obj': point_obj,
                'point_log_obj': point_log_obj,  # 이거를 넘기면 첫 포인트 로그 생성시 값들이 넘어간다. 갱신되는 값에는 적용 못한다.
                'prep_point': cart.prep_point(),
                'used_point': cart.used_point(),
                'remained_point': cart.remained_point(),
                'new_remained_point': cart.new_remained_point(),  # used_point 가 없을 때 사용하기 위해 템플릿으로 넘긴다.
            }
            return render_template('ecomm/carts/cart_view.html', context=context)
        else:
            abort(401)
    else:
        abort(401)


cartproductoption = ""


@carts_bp.route('/cart/update/ajax', methods=['POST'])
@login_required
def cart_update_ajax():
    global cartproductoption
    if request.method == 'POST':
        cart_id = request.form.get("cart_id")
        product_id = request.form.get("product_id")
        product_count = request.form.get("product_count")
        product_total_price = request.form.get("product_total_price")

        option_id = request.form.getlist("option_id[]")
        option_count = request.form.getlist("option_count[]")
        option_line_price = request.form.getlist("option_total_price[]")
        print(option_id)
        print(option_count)

        cartproduct = CartProduct.query.filter_by(cart_id=cart_id, product_id=product_id).first()

        cartproduct.product_subtotal_quantity = 0
        cartproduct.product_subtotal_price = 0
        cartproduct.op_subtotal_price = 0
        cartproduct_update(cartproduct, product_count, product_total_price)
        db.session.add(cartproduct)

        op_count_dict = dict()
        op_id = list()# []
        op_count = list()#[]
        if option_id:
            for idx in range(len(option_id)):
                cartproductoption = CartProductOption.query.filter_by(cart_id=cart_id, option_id=option_id[idx]).first()

                if cartproductoption:
                    cartproductoption.op_quantity = 0
                    cartproductoption.op_line_price = 0
                    cartproductoption.op_quantity += int(option_count[idx])
                    cartproductoption.op_line_price += int(option_line_price[idx])
                    db.session.bulk_save_objects([cartproductoption])
                else:
                    option_obj = ProductOption.query.get_or_404(option_id[idx])
                    new_cartproductoption = CartProductOption(cart_id=cart_id, product_id=product_id)
                    new_cartproductoption_create(new_cartproductoption, option_obj, idx, option_id, option_count, option_line_price)
                    db.session.bulk_save_objects([new_cartproductoption])

                op_id.append(option_id[idx])
                op_count.append(option_count[idx])

                cartproduct.op_subtotal_price += int(option_line_price[idx])
                cartproduct.line_price = cartproduct.product_subtotal_price + cartproduct.op_subtotal_price
                db.session.add(cartproduct)
        db.session.commit()

        update_data_response = {
            "product_id": product_id,
            "product_count": product_count,
            "product_total_price": product_total_price,

            "op_id": op_id,
            "op_count": op_count,
            "cartproduct_op_subtotal_price": cartproduct.op_subtotal_price,
            "cartproduct_line_price": cartproduct.line_price,
        }
        return make_response(jsonify(update_data_response))


@carts_bp.route('/cart/option/delete/ajax', methods=['POST'])
@login_required
def cart_option_delete_ajax():
    if request.method == 'POST':
        cart_id = request.form.get("cart_id")
        product_id = request.form.get("product_id")
        option_id = request.form.get("option_id")
        cart = Cart.query.get_or_404(cart_id)

        cartproduct = CartProduct.query.filter_by(cart_id=cart_id, product_id=product_id).first()
        cartproductoption = CartProductOption.query.filter_by(cart_id=cart_id, option_id=option_id).first()

        cartproduct.op_subtotal_price = cartproduct.op_subtotal_price - cartproductoption.op_line_price
        cartproduct.line_price = cartproduct.line_price - cartproductoption.op_line_price
        cart.cart_total_price = cart.cart_total_price - cartproductoption.op_line_price
        db.session.add(cart)
        db.session.add(cartproduct)

        db.session.delete(cartproductoption)
        db.session.commit()
        delete_data_response = {
            "_success": "delete_success",
            "cart_pd_line_price": cartproduct.line_price,
        }
        return make_response(jsonify(delete_data_response))


@carts_bp.route('/cart/product/delete/ajax', methods=['POST'])
@login_required
def cart_product_delete_ajax():
    if request.method == 'POST':
        cart_id = request.form.get("cart_id")
        product_id = request.form.get("product_id")
        cart = Cart.query.get_or_404(cart_id)
        cartproduct = CartProduct.query.filter_by(cart_id=cart_id, product_id=product_id).first()
        if cartproduct:
            cart.cart_total_price = cart.cart_total_price - cartproduct.line_price
            db.session.add(cart)
            cartproductoptions = CartProductOption.query.filter_by(cart_id=cart_id, product_id=product_id).all()
            if cartproductoptions:
                for cartpdop in cartproductoptions:
                    db.session.delete(cartpdop)
                db.session.delete(cartproduct)
            else:
                db.session.delete(cartproduct)
        db.session.commit()
        print(cart.cart_total_price)

        point_ratio = VarRatio.query.get(2).ratio
        point_obj = Point.query.filter_by(user_id=current_user.id).first()
        point_log = PointLog.query.filter_by(cart_id=cart.id).first()

        will_dct_amount = cart.discount_total_amount()
        new_prep_point = round(float(cart.subtotal_price() - will_dct_amount) * float(point_ratio))
        point_log_update(cart, point_obj, point_log, point_log.used_point, new_prep_point)

        delete_data_response = {
            "_success": "delete_success",
            'prep_point': point_log.prep_point,
            'new_remained_point': point_log.new_remained_point,
            "cart_total_price": cart.cart_total_price,
            "cart_pay_price": cart.get_total_price()
        }
        return make_response(jsonify(delete_data_response))