from flask_login import current_user
from flask import abort, request

from flask_www.accounts.utils import login_required
from flask_www.configs import db
from flask_www.ecomm.promotions.models import Coupon, PointLog, Point

coupon_obj = ''
new_point_log_obj = ''


@login_required
def coupon_code_check(req_code):
    existing_coupon = Coupon.query.filter_by(code=req_code).first()
    if existing_coupon:
        code_check_response = {
            "flash_message": "동일한 쿠폰코드가 존재합니다.",
        }
    else:
        code_check_response = {
            "flash_message": "사용가능한 쿠폰코드입니다.",
        }
    return code_check_response


@login_required
def coupon_count_update(used_coupons):
    global coupon_obj
    for used_coupon in used_coupons:
        coupon_obj = Coupon.query.get_or_404(used_coupon.coupon_id)
        coupon_obj.used_count += 1
        coupon_obj.available_count -= 1
    db.session.bulk_save_objects([coupon_obj])
    db.session.commit()


@login_required
def new_point_log_create(cart, point_obj):
    new_point_log = PointLog(user_id=current_user.id)
    new_point_log.point_id = point_obj.id,

    new_point_log.cart_id = cart.id,
    new_point_log.prep_point = cart.prep_point(),
    new_point_log.new_remained_point = (cart.remained_point() + cart.prep_point())
    db.session.add(new_point_log)
    db.session.commit()
    print('000000000000000000000000000000', new_point_log)
    cart.point_log_id = new_point_log.id
    current_db_sessions = db.session.object_session(cart)
    current_db_sessions.add(cart)
    db.session.commit()
    return new_point_log


@login_required
def cart_point_log_create(cart):
    global new_point_log_obj
    try:
        point_obj = Point.query.filter_by(user_id=current_user.id).first()
        point_log_obj = PointLog.query.filter_by(cart_id=cart.id).first()
    except Exception as e:
        print(e, '포인트 객체 혹은 유저인증이 않됬거나, 카트 객체가 없다.')
        point_obj = None
        point_log_obj = None
    if not point_obj and not point_log_obj:
        new_point_obj = Point(user_id=current_user.id)
        db.session.add(new_point_obj)
        db.session.commit()
        new_point_log_obj = new_point_log_create(cart, new_point_obj)

    elif point_obj and not point_log_obj:
        new_point_log_obj = new_point_log_create(cart, point_obj)

    elif point_obj and point_log_obj:
        point_log_obj.prep_point = cart.prep_point()
        if not point_log_obj.used_point:
            point_log_obj.new_remained_point = (point_obj.remained_point + cart.prep_point())
        else:
            point_log_obj.new_remained_point = (point_obj.remained_point + cart.prep_point() - int(point_log_obj.used_point))

        current_db_sessions = db.session.object_session(point_log_obj)
        current_db_sessions.add(point_log_obj)
        db.session.commit()
    else:
        abort(404)

    return new_point_log_obj or point_log_obj


@login_required
def point_log_update(cart, point_obj, point_log, used_point, new_prep_point):
    """포인트 apply 과정에서, 포인트로그 객체를 수정하는 과정을 담는다."""
    point_log.used_point = used_point
    point_log.prep_point = new_prep_point
    point_log.new_remained_point = point_obj.remained_point - int(point_log.used_point) + int(new_prep_point)
    point_log.user_id = current_user.id
    point_log.cart_id = cart.id
    current_db_sessions = db.session.object_session(point_log)
    current_db_sessions.add(point_log)
    db.session.commit()

    cart.point_log_id = point_log.id
    current_db_sessions = db.session.object_session(cart)
    current_db_sessions.add(cart)
    db.session.commit()


@login_required
def order_point_update(cart, point_obj):
    """결제하면 order_imp_transaction 에서 적용된다."""
    exist_total_accum_point = point_obj.total_accum_point #old
    exist_remained_point = point_obj.remained_point #old
    point_log_obj = PointLog.query.get(cart.point_log_id)
    if cart.point_log_id and point_log_obj:
        print('if cart.point_log_id')
        point_obj.total_accum_point += point_log_obj.prep_point
        point_obj.remained_point = point_log_obj.new_remained_point
        current_db_sessions = db.session.object_session(point_log_obj)
        current_db_sessions.add(point_log_obj)
        db.session.commit()
        # old_total_accum_point = point_obj.total_accum_point
        # Point.query.update(total_accum_point=old_total_accum_point + point_log_obj.prep_point,
        #                    remained_point=point_log_obj.remained_point
        #                    )

    if not cart.point_log_id:
        '''이런 경우는 존재하지 않겠네... 로직상 이 지점에 도달하지도 않겠네...
        카트에 담는 순간에 (add_to_cart_ajax)
        point_log 객체와 cart 에 그에 따른 point_log_id를 생성해버리니까...'''
        print('if not cart.point_log_id')
        point_log_obj = PointLog.query.filter_by(point_id=point_obj.id, cart_id=cart.id).first()  # add_to_cart_ajax때 이미 생성해왔다.
        try:
            ot_ap = int(exist_total_accum_point)
        except TypeError:
            ot_ap = 0  # point가 아예 없는 초출인 경우 old_total_accum_point은 None--->0으로 바꾸는 과정
        try:
            o_rp = int(exist_remained_point)
        except TypeError:
            o_rp = 0  # point가 아예 없는 초출인 경우 old_remained_point은 None--->0으로 바꾸는 과정
        point_obj.total_accum_point = ot_ap + point_log_obj.prep_point
        point_obj.remained_point = o_rp + point_log_obj.prep_point
        db.session.add(point_obj)
        db.session.commit()

        point_log_obj.remained_point = point_obj.remained_point  ## 최종 적립후 로그기록  거꾸로 보완 추가저장
        db.session.add(point_log_obj)
        db.session.commit()