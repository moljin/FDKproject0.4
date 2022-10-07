from flask import Blueprint, request, make_response, jsonify, redirect, url_for, abort
from flask_login import current_user

from flask_www.accounts.utils import login_required
from flask_www.commons.models import VarRatio, BaseAmount
from flask_www.configs import db
from flask_www.ecomm.carts.models import Cart
from flask_www.ecomm.promotions.models import UsedCoupon, Point, PointLog
from flask_www.ecomm.promotions.utils import point_log_update, cart_point_log_create

NAME = 'points'
points_bp = Blueprint(NAME, __name__, url_prefix='/promotions/points')


@points_bp.route('/apply/ajax', methods=['POST'])
@login_required
def apply_point_ajax():
    cart_id = request.form.get("cart_id")
    used_point = request.form['used_point']  # <class 'str'>
    cart = Cart.query.get_or_404(cart_id)
    used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
    used_coupon_total_amount = cart.coupon_discount_total()
    point_ratio = VarRatio.query.get_or_404(2).ratio
    try:
        point_obj = Point.query.filter_by(user_id=current_user.id).first()
    except Exception as e:
        print("apply_point_ajax() Exception Error:: ", e)
        point_obj = None
        cart.point_log_id = None
        db.session.add(cart)
        db.session.commit()

    if request.method == "POST" and current_user.is_authenticated:
        base_pay_amount = BaseAmount.query.get(1).amount
        point_log = PointLog.query.filter_by(cart_id=cart.id).first()

        if used_coupons:  # dct=discount total
            will_dct_amount = used_coupon_total_amount + int(used_point)
            new_prep_point = (cart.cart_total_price - will_dct_amount) * point_ratio  # <class 'decimal.Decimal'>
            if int(used_point) <= point_obj.remained_point and cart.cart_total_price >= will_dct_amount + base_pay_amount:
                point_log_update(cart, point_obj, point_log, used_point, new_prep_point)
                message = '포인트가 적용되었어요!'

            elif int(used_point) <= point_obj.remained_point and cart.cart_total_price < will_dct_amount + base_pay_amount:
                print('xxx11111 최소 결제금액이 500원이상은 되어야 해요!')
                message = '최소 결제금액이 500원이상은 되어야 해요!'

            elif int(used_point) > point_obj.remained_point:
                message = '잔여포인트를 초과했어요!'

            else:
                print('extra')
                message = '포인트가 적용되지 않았어요!'
        else:
            will_dct_amount = int(used_point)
            new_prep_point = (cart.cart_total_price - int(used_point)) * point_ratio
            print('nnnnnnnnnnnnnnnnnn=new_prep_point', new_prep_point)
            if int(used_point) <= point_obj.remained_point and cart.cart_total_price >= int(used_point) + base_pay_amount:
                point_log_update(cart, point_obj, point_log, used_point, new_prep_point)
                print('222')
                message = '포인트가 적용되었어요!'

            elif int(used_point) <= point_obj.remained_point and cart.cart_total_price < int(used_point) + base_pay_amount:
                print('2.xxxxxxxxxxxxxx 최소 결제금액이 500원이상은 되어야 해요!')
                message = '최소 결제금액이 500원이상은 되어야 해요!'

            elif int(used_point) > point_obj.remained_point:
                message = '잔여포인트를 초과했어요!'

            else:
                message = '포인트가 적용되지 않았어요!'
        print('new_remained_point', point_obj.remained_point - int(point_log.used_point) + int(new_prep_point))
        cart_point_log_create(cart)
        context = {'cart_id': cart.id,
                   'flash_message': message,
                   'used_point': used_point,  # 할인 적용포인트
                   'prep_point': int(new_prep_point),  # 적립 예정포인트
                   'dct_amount': will_dct_amount,  # 총 할인금액
                   'new_remained_point': point_obj.remained_point - int(point_log.used_point) + int(new_prep_point),
                   'point_log_id': cart.point_log_id,
                   # 'cart_new_remained_point': cart.new_remained_point(), # 없어도 된다. 있으면 에러 발생
                   # cart.new_remained_point(): unsupported operand type(s) for -: 'int' and 'str'
                   # 'pointlog_new_remained_point': cart.new_remained_point(),
                   # 최종 예정 적립포인트
                   'sell_charge': cart.sell_charge_amount(),
                   'get_total_price': cart.get_total_price()
                   }
        return make_response(jsonify(context))
    elif request.method == "POST" and not current_user.is_authenticated:
        path_redirect = request.form.get('next')  # .split('?next=/')  # , 1)
        return redirect(url_for('accounts.login' + '?next=' + path_redirect))
    else:
        abort(401)


@points_bp.route('/cancel/ajax', methods=['POST'])
@login_required
def cancel_point_ajax():
    if request.method == "POST":
        point_log_id = request.form['cart_point_log_id']
        point_log = PointLog.query.get(point_log_id)

        point_log.new_remained_point += point_log.used_point
        point_log.used_point = 0

        current_db_sessions = db.session.object_session(point_log)
        current_db_sessions.add(point_log)
        db.session.commit()

        cart_id = request.form.get('cart_id')
        cart = Cart.query.get_or_404(cart_id)

        context = {
            'flash_message': "포인트적용이 취소되었습니다.",
            'prep_point': cart.prep_point(),
            'new_remained_point': cart.new_remained_point(),
            'get_total_price': cart.get_total_price()
        }
        return make_response(jsonify(context))

