from flask import Blueprint, request, g, make_response, jsonify, render_template
from flask_login import current_user
from sqlalchemy import desc

from flask_www.accounts.utils import login_required
from flask_www.configs import db
from flask_www.configs.config import NOW
from flask_www.ecomm.carts.models import Cart, CartProduct, CartProductOption
from flask_www.ecomm.orders.forms import OrderCreateForm
from flask_www.ecomm.orders.models import Order, OrderCoupon, OrderProduct, OrderProductOption, OrderTransaction, ORDER_STATUS
from flask_www.ecomm.orders.utils import order_transaction_create, product_stock_update, product_option_stock_update, iamport_client_validation
from flask_www.ecomm.promotions.models import PointLog, UsedCoupon, Point
from flask_www.ecomm.promotions.utils import coupon_count_update, order_point_update

NAME = 'orders'
orders_bp = Blueprint(NAME, __name__, url_prefix='/orders')


@orders_bp.route('/create/ajax', methods=['POST'])
@login_required
def order_create_ajax():
    cart = Cart.query.filter_by(id=request.form.get("ordercart_id")).first()
    try:
        user_id = current_user.id
    except:
        user_id = None
    cart_productitems = CartProduct.query.filter_by(cart_id=cart.id).all()
    cart_optionitems = CartProductOption.query.filter_by(cart_id=cart.id).all()
    form = OrderCreateForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            point_log = PointLog.query.filter_by(cart_id=cart.id).first()
        except Exception as e:
            print(e, 'no used_point')
            point_log = None
        new_order = Order(
            order_num=NOW.strftime('%Y%m%d%H%M%S%f'),
            user_id=user_id,
            cart_id=cart.id,
            name=request.form.get('name'),
            email=request.form.get('email'),
            phonenumber=request.form.get('phonenumber'),
            postal_code=request.form.get('postal_code'),
            address=request.form.get('address'),
            detail_address=request.form.get('detail_address'),
            extra_address=request.form.get('extra_address'),
            order_memo=request.form.get('order_memo'),
            used_point=point_log.used_point,
            get_point=cart.prep_point(),
            total_discount_amount=cart.discount_total_amount(),
            total_order_amount=cart.subtotal_price(),
            get_total_amount=cart.get_total_price(),
            total_delivery_pay_amount=cart.get_total_delivery_pay(),
            real_paid_amount=cart.get_real_pay_price()
        )
        g.db.add(new_order)
        g.db.commit()
        used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
        if used_coupons:
            for used_coupon in used_coupons:
                new_order_coupon = OrderCoupon(
                    order_id=new_order.id,
                    coupon_id=used_coupon.coupon_id,
                    code=used_coupon.code,
                    amount=used_coupon.amount,
                    owner_id=used_coupon.owner_id,
                    consumer_id=used_coupon.consumer_id
                )
                g.db.bulk_save_objects([new_order_coupon])
            g.db.commit()
        for cart_productitem in cart_productitems:
            new_order_productitem = OrderProduct(
                order_id=new_order.id,
                product_id=cart_productitem.product_id,
                pd_price=cart_productitem.price,
                pd_subtotal_price=cart_productitem.product_subtotal_price,
                pd_subtotal_quantity=cart_productitem.product_subtotal_quantity,
                op_subtotal_price=cart_productitem.op_subtotal_price,
                line_price=cart_productitem.line_price
            )
            g.db.bulk_save_objects([new_order_productitem])
        g.db.commit()
        if cart_optionitems:
            for cart_optionitem in cart_optionitems:
                new_order_optionitem = OrderProductOption(
                    order_id=new_order.id,
                    orderproduct_product_id=cart_optionitem.product_id,
                    option_id=cart_optionitem.option_id,
                    op_title=cart_optionitem.title,
                    op_price=cart_optionitem.price,
                    op_quantity=cart_optionitem.op_quantity,
                    op_line_price=cart_optionitem.op_line_price
                )
                g.db.bulk_save_objects([new_order_optionitem])
            g.db.commit()
            pass
        data = {'order_id': new_order.id}
        return make_response(jsonify(data), 200)
    else:
        message = '어딘가 올바르지 않게 입력되었어요!!'
        return make_response(jsonify({'message': message}), 401)


@orders_bp.route('/checkout/ajax', methods=['POST'])
@login_required
def order_checkout_ajax():
    order_id = request.form['order_id']
    order = Order.query.filter_by(id=order_id).first()
    paid_amount = request.form['amount']

    try:
        print('저기1 order_id', order_id)
        merchant_order_id = order_transaction_create(order_id=order_id, amount=paid_amount)
        print("저기2: merchant_order_id: ", merchant_order_id)
    except Exception as e:
        print(e)
        merchant_order_id = None

    if merchant_order_id is not None:
        data = { # checkout.js: OrderCheckoutAjax 로 넘기는 data
            "works": True,
            "merchant_id": merchant_order_id# + '@' + str(uuid.uuid4()) + NOW.microsecond#
        }
        print("0000000000000000000 여기3 data", data)  # 결제하기를 누르면 여기까지(결제창이 뜸) 진행된다.
        return make_response(jsonify(data), 200)
    else:
        message = 'order_checkout_ajax'
        return make_response(jsonify({'message': message}), 401)


@orders_bp.route('/imp/ajax', methods=['POST'])
@login_required
def order_imp_transaction():
    cart = Cart.query.filter_by(id=request.form.get("cart_id")).first()
    order_id = request.form['order_id']
    order = Order.query.filter_by(id=order_id).first()

    order_productitems = OrderProduct.query.filter_by(order_id=order_id).all()
    order_optionitems = OrderProductOption.query.filter_by(order_id=order_id).all()
    if order_productitems and not order_optionitems:
        product_stock_update(order_productitems)
    if order_productitems and order_optionitems:
        product_option_stock_update(order_productitems, order_optionitems)

    used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
    if used_coupons:
        coupon_count_update(used_coupons)

    point_obj = Point.query.filter_by(user_id=current_user.id).first() # 카트에 담을때 이미 포인트객체를 만들어 놓는다.
    if point_obj:
        order_point_update(cart, point_obj)

    # # 구매 메일링 여기에 넣으면 될 듯...

    # origin_merchant_id = request.POST.get('merchant_id').split("@")[0]
    merchant_id = request.form['merchant_id']
    imp_id = request.form['imp_id']
    amount = request.form['amount']
    print('class OrderImpAjaxView;;;order', order)
    print("class OrderImpAjaxView;;;merchant_id", merchant_id)
    print("class OrderImpAjaxView;;;imp_id", imp_id)
    print('class OrderImpAjaxView;;;amount', amount)

    try:
        trans = OrderTransaction.query.filter_by(
            order_id=order_id,
            merchant_order_id=merchant_id,
            amount=amount
        ).first()
    except:
        trans = None

    if trans is not None:
        trans.transaction_id = imp_id
        trans.is_success = True
        trans.transaction_status = "OK"
        current_db_sessions = db.session.object_session(trans)
        current_db_sessions.add(trans)

        order.is_paid = True
        order.order_status = ORDER_STATUS[1]
        current_db_sessions = db.session.object_session(order)
        current_db_sessions.add(order)
        db.session.commit()
        print('00000000000 ;;iamport_client_;; order_payment_validation 이 위치에서 실행된다.')
        iamport_client_validation(merchant_id, order_id)

        data = {
            "works": True,
            "order_id": order_id
        }

        print("여기3333")
        print('OrderImpAjaxView :::data', data)
        # cart.delete()
        cart.is_active = False
        cart.cart_id = '주문완료된 카트'
        current_db_sessions = db.session.object_session(cart)
        current_db_sessions.add(cart)
        db.session.commit()

        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify({}), 401)


@orders_bp.route('/complete/detail', methods=['GET'])
@login_required
def order_complete_detail():
    order_id = request.full_path.split('=')[1] #ajax reload url의 full_path에서 잘라냄
    order = Order.query.filter_by(id=order_id).first()
    order_productitems = OrderProduct.query.filter_by(order_id=order_id).all()
    order_optionitems = OrderProductOption.query.filter_by(order_id=order_id).all()
    order_coupons = OrderCoupon.query.filter_by(order_id=order_id).all()
    print(type(order))
    print("order_productitems", order_productitems)
    print("order_optionitems", order_optionitems)
    print("order_coupons", order_coupons)
    return render_template('ecomm/orders/order_complete_detail.html',
                           order=order,
                           order_productitems=order_productitems,
                           order_optionitems=order_optionitems,
                           order_coupons=order_coupons)


@orders_bp.route('/complete/list', methods=['GET'])
@login_required
def order_complete_list():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(desc(Order.created_at)).all()
    order_coupons = OrderCoupon.query.all()

    return render_template('ecomm/orders/order_complete_list.html', orders=orders)