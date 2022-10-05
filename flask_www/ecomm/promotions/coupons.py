from flask import Blueprint, redirect, url_for, render_template, g, request
from flask_login import current_user
from sqlalchemy import desc

from flask_www.accounts.models import User, Profile
from flask_www.accounts.utils import vendor_required
from flask_www.commons.ownership_required import coupon_ownership_required
from flask_www.configs import db
from flask_www.ecomm.promotions.forms import CouponCreateForm
from flask_www.ecomm.promotions.models import Coupon

NAME = 'coupons'
coupons_bp = Blueprint(NAME, __name__, url_prefix='/promotions/coupons')


@coupons_bp.route('/create', methods=['GET'])
@vendor_required
def create():
    form = CouponCreateForm()
    return render_template('ecomm/promotions/coupons/create.html', form=form)


@coupons_bp.route('/save', methods=['POST'])
@vendor_required
def save():
    # code 중복 확인하는 코드가 필요하다.
    form = CouponCreateForm()
    code = form.code.data
    use_from = form.use_from.data
    use_to = form.use_to.data
    amount = form.amount.data
    available_count = form.available_count.data
    is_active = form.is_active.data
    if form.validate_on_submit():
        new_coupon = Coupon(
            user_id=current_user.id,
        )
        new_coupon.code = code
        new_coupon.use_from = use_from
        new_coupon.use_to = use_to
        new_coupon.amount = amount
        new_coupon.is_active = is_active
        new_coupon.available_count = available_count

        g.db.add(new_coupon)
        g.db.commit()
        return redirect(url_for('coupons.detail', _id=new_coupon.id))


@coupons_bp.route('/detail/<int:_id>', methods=['GET'])
@coupon_ownership_required
def detail(_id):
    coupon_obj = db.session.query(Coupon).filter_by(id=_id).first()
    owner_id = coupon_obj.user_id
    owner_obj = User.query.get_or_404(owner_id)
    return render_template('ecomm/promotions/coupons/detail.html', coupon_owner=owner_obj, coupon=coupon_obj)


# @coupon_ownership_required 가 가장 상위의 제한조건이므로 vendor_required 는 굳이 없어도 될듯...
@coupons_bp.route('/list/<int:_id>', methods=['GET'])
# @coupon_ownership_required  # 여기서 막아버리면 판매사업자가 쿠폰을 만들지 않았을 때 로드되지 않는다.(404)
def _list(_id):
    user_obj = User.query.get_or_404(_id)
    profile_obj = Profile.query.filter_by(user_id=_id).first()
    page = request.args.get('page', type=int, default=1)
    coupons = Coupon.query.filter_by(user_id=_id).order_by(desc(Coupon.created_at))  # id))  # .all()
    # try:
    #     coupons = Coupon.query.filter_by(user_id=pk_id).order_by(desc(Coupon.created_at))#id))  # .all()
    # except:
    #     coupons = None

    """
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        sub_query = db_session.query(Answer.question_id,
                                     Answer.content,
                                     Profile.nickname).join(Profile, Answer.user_id == Profile.user_id).subquery()
        print('00000000000000000000000==sub_query', sub_query)
        questions = questions.join(User, Profile).outerjoin(sub_query, sub_query.c.question_id == Question.id)\
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    Profile.nickname.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.nickname.ilike(search)).distinct()  # 답변작성자
        """
    pagination = coupons.paginate(page, per_page=10, error_out=False)
    c_list = pagination.items
    return render_template('ecomm/promotions/coupons/list.html', coupons=c_list, pagination=pagination, user=user_obj,
                           profile=profile_obj)  # , kw=kw)




