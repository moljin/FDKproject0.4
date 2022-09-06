import os
import shutil

from flask import Blueprint, g, redirect, url_for, render_template, request, abort, session, make_response, jsonify, flash
from flask_login import current_user
from sqlalchemy import desc

from flask_www.accounts.forms import ProfileForm, VendorForm, VendorAjaxForm
from flask_www.accounts.models import Profile, User, LEVELS, ProfileCoverImage
from flask_www.accounts.utils import login_required, send_mail_for_any, profile_delete
from flask_www.commons.ownership_required import profile_ownership_required
from flask_www.commons.utils import save_file, ajax_post_key, flash_form_errors
from flask_www.configs import db
from flask_www.configs.config import NOW, BASE_DIR
from flask_www.ecomm.products.models import ShopCategory

NAME = 'profiles'
profiles_bp = Blueprint(NAME, __name__, url_prefix='/accounts')

data_response = ""


@profiles_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProfileForm()
    nickname = form.nickname.data
    existing_nickname = Profile.query.filter_by(nickname=nickname).first()
    message = form.message.data
    profile_image = form.data.get('profile_image')
    try:
        if existing_nickname:
            flash("동일한 닉네임이 존재합니다.")
        elif form.validate_on_submit():
            new_profile = Profile(
                nickname=nickname,
                message=message,
                user_id=g.user.id
            )
            # if profile_image:
            #     relative_path, _ = save_file(NOW, profile_image)
            #     new_profile.image_path = relative_path
            #     print(new_profile.image_path)
            db.session.add(new_profile)
            db.session.commit()
            return redirect(url_for('profiles.detail', _id=new_profile.id))
        else:
            flash_form_errors(form)
    except Exception as e:
        print(e)
    return render_template('accounts/profiles/profile_create.html', form=form)


@profiles_bp.route('/profile_images/save/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def profile_img_save_ajax(_id):
    ajax_post_key()
    post_key = session["ajax_post_key"]

    profile = db.session.query(Profile).filter_by(id=_id).first()
    existing_profile_img = profile.image_path
    profile_image = request.files.get('profile_image')
    if post_key and request.method == 'POST':
        if existing_profile_img:
            relative_path, upload_path = save_file(NOW, profile_image)
            if profile_image:
                old_image_path = os.path.join(BASE_DIR, existing_profile_img)
                if old_image_path != upload_path:
                    if os.path.isfile(old_image_path):
                        shutil.rmtree(os.path.dirname(old_image_path))
            profile.image_path = relative_path
        else:
            if profile_image:
                relative_path, _ = save_file(NOW, profile_image)
                profile.image_path = relative_path
        db.session.add(profile)
        db.session.commit()
        session.pop('ajax_post_key', None)
        profile_data_response = {
            "image_path": profile.image_path,
        }
        return make_response(jsonify(profile_data_response))
    abort(401)


@profiles_bp.route('/profile_images/delete/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def profile_img_delete_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    existing_profile_img = profile.image_path
    if request.method == 'POST':
        if existing_profile_img:
            try:
                old_image_path = os.path.join(BASE_DIR, existing_profile_img)
                if os.path.isfile(old_image_path):
                    shutil.rmtree(os.path.dirname(old_image_path))
                profile.image_path = ""
            except Exception as e:
                print(e)
        db.session.add(profile)
        db.session.commit()
        profile_data_response = {
            "image_path": "static/statics/images/user_none.png" # 맨앞 / 를 빼고 넘긴다. ...
        }
        return make_response(jsonify(profile_data_response))
    abort(401)


@profiles_bp.route('/profile/detail/<int:_id>', methods=['GET'])
def detail(_id):
    profile_obj = db.session.query(Profile).filter_by(id=_id).first()
    user_id = profile_obj.user_id
    user_obj = User.query.get_or_404(user_id)
    cover_img_obj = db.session.query(ProfileCoverImage).filter_by(profile_id=profile_obj.id).first()
    shopcategory_objs = db.session.query(ShopCategory).filter_by(user_id=user_obj.id).all()  # .order_by(desc(ShopCategory.created_at))
    return render_template('accounts/profiles/profile_detail.html', target_profile_user=user_obj, target_profile=profile_obj, shopcategory_objs=shopcategory_objs, cover_img=cover_img_obj)


@profiles_bp.route('/profile/vendor/not', methods=['GET'])
@login_required
def vendor_not():
    _id = current_user.id
    user_obj = User.query.get_or_404(_id)
    profile_obj = Profile.query.filter_by(user_id=user_obj.id).first()
    return render_template('accounts/profiles/vendor_not.html', user=user_obj, profile=profile_obj)


@profiles_bp.route('/profile/update/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def update_ajax(_id):
    global data_response
    user_id = current_user.id
    profile = db.session.query(Profile).filter_by(user_id=user_id).one()
    if request.method == 'POST':
        if profile:
            nickname = request.form.get("nickname")
            message = request.form.get("message")
            existing_nickname = Profile.query.filter_by(nickname=nickname).first()
            if existing_nickname:
                if nickname != profile.nickname:
                    nickname_data_response = {
                        "flash_message": "동일한 닉네임이 존재합니다.",
                    }
                    return make_response(jsonify(nickname_data_response))
            if nickname and message:
                profile.nickname = nickname
                profile.message = message
                # profile_image = request.files.get('profile_image')
            # if profile_image:
            #     profile_image_relative_path, profile_image_upload_path = save_file(NOW, profile_image)
            #     if profile.image_path:
            #         profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
            #         if profile_image_origin_path != profile_image_upload_path:
            #             if os.path.isfile(profile_image_origin_path):
            #                 shutil.rmtree(os.path.dirname(profile_image_origin_path))
            #     profile.image_path = profile_image_relative_path
                db.session.add(profile)
                db.session.commit()

                profile_data_response = {
                    "profile_nickname": profile.nickname,
                    "profile_message": profile.message,
                    # "profile_image_path": profile.image_path,
                }
                return make_response(jsonify(profile_data_response))
            elif not nickname:
                data_response = {
                    "checked_message": "닉네임를 채워주세요!",
                }
            elif not message:
                data_response = {
                    "checked_message": "간단 메시지를 채워주세요!",
                }
            return make_response(jsonify(data_response))
        else:
            abort(401)


@profiles_bp.route('profile/vendor/detail/<int:_id>', methods=['GET'])
@login_required
def vendor_detail(_id):
    form = VendorForm()
    profile_obj = db.session.query(Profile).filter_by(id=_id).first()
    user_obj = db.session.query(User).filter_by(id=profile_obj.user_id).first()
    cover_img_obj = db.session.query(ProfileCoverImage).filter_by(profile_id=profile_obj.id).first()
    shopcategory_objs = db.session.query(ShopCategory).filter_by(user_id=user_obj.id).all()  # .order_by(desc(ShopCategory.created_at))
    return render_template('accounts/profiles/profile_detail.html', target_profile_user=user_obj, target_profile=profile_obj, shopcategory_objs=shopcategory_objs, cover_img=cover_img_obj, form=form)


@profiles_bp.route('/profile/vendor/corp-image/save/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_corp_image_save_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    corp_image = request.files.get('corp_image')
    corp_image_save(profile, corp_image)
    db.session.add(profile)
    db.session.commit()
    corp_img_data_response = {
        "success_msg": "Success"
    }
    return make_response(jsonify(corp_img_data_response))


def corp_image_save(profile, corp_image):
    corp_image_relative_path, corp_image_upload_path = save_file(NOW, corp_image)
    if profile.corp_image_path:
        corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
        if corp_image_origin_path != corp_image_upload_path:
            if os.path.isfile(corp_image_origin_path):
                shutil.rmtree(os.path.dirname(corp_image_origin_path))
    profile.corp_image_path = corp_image_relative_path


@profiles_bp.route('/profile/vendor/update/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_update_ajax(_id):
    global data_response
    profile = db.session.query(Profile).filter_by(id=_id).first()
    level = profile.level
    if request.method == 'POST':
        if profile:
            corp_brand = request.form.get("corp_brand")
            corp_email = request.form.get("corp_email")
            corp_number = request.form.get("corp_number")
            corp_online_marketing_number = request.form.get("corp_online_marketing_number")
            corp_address = request.form.get("corp_address")
            main_phonenumber = request.form.get("main_phonenumber")
            main_cellphone = request.form.get("main_cellphone")
            corp_image = request.files.get('corp_image')

            existing_corp_brand = Profile.query.filter_by(corp_brand=corp_brand).first()            # if corp_brand:  # != profile.corp_brand:
            if existing_corp_brand:
                if corp_brand != profile.corp_brand:
                    data_response = {
                        "checked_message": "동일한 상호명이 존재합니다.",
                    }
                    return make_response(jsonify(data_response))

            if corp_brand and corp_email and corp_number and corp_online_marketing_number and corp_address and main_phonenumber and main_cellphone:

                req_level = request.form.get('level')
                if req_level == level:
                    if profile.level == "일반이용자":
                        profile.level = LEVELS[1]

                profile.corp_brand = corp_brand
                profile.corp_email = corp_email
                profile.corp_number = corp_number
                profile.corp_online_marketing_number = corp_online_marketing_number
                profile.corp_address = corp_address
                profile.main_phonenumber = main_phonenumber
                profile.main_cellphone = main_cellphone
                if corp_image:
                    corp_image_save(profile, corp_image)
                    # corp_image_relative_path, corp_image_upload_path = save_file(NOW, corp_image)
                    # if profile.corp_image_path:
                    #     corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                    #     if corp_image_origin_path != corp_image_upload_path:
                    #         if os.path.isfile(corp_image_origin_path):
                    #             shutil.rmtree(os.path.dirname(corp_image_origin_path))
                    # profile.corp_image_path = corp_image_relative_path
                elif not corp_image:
                    if not profile.corp_image_path:
                        data_response = {
                            "checked_message": "사업자등록증을 채워주세요!",
                        }
                        return make_response(jsonify(data_response))

                db.session.add(profile)
                db.session.commit()

                subject = "판매사업자 신청 메일"
                user_email = current_user.email
                token = None
                msg_txt = 'accounts/send_mails/account_update_register_mail.txt'
                msg_html = 'accounts/send_mails/account_update_register_mail.html'
                send_mail_for_any(subject, user_email, token, msg_txt, msg_html)

                data_response = {
                    "corp_brand": profile.corp_brand,
                    "corp_email": profile.corp_email,
                    "corp_number": profile.corp_number,
                    "corp_online_marketing_number": profile.corp_online_marketing_number,
                    "corp_image_path": profile.corp_image_path,
                    "corp_address": profile.corp_address,
                    "main_phonenumber": profile.main_phonenumber,
                    "main_cellphone": profile.main_cellphone,
                    "profile_level": profile.level
                }

                return make_response(jsonify(data_response))
            elif not corp_brand:
                data_response = {
                    "checked_message": "상호명을 채워주세요!",
                }
                # return make_response(jsonify(data_response))
            elif not corp_email:
                data_response = {
                    "checked_message": "사업자용 이메일을 채워주세요!",
                }
                # return make_response(jsonify(data_response))
            elif not corp_number:
                data_response = {
                    "checked_message": "사업자등록번호를 채워주세요!",
                }
                # return make_response(jsonify(data_response))
            elif not corp_online_marketing_number:
                data_response = {
                    "checked_message": "통신판매업번호를 채워주세요!",
                }
                # return make_response(jsonify(data_response))
            elif not corp_address:
                data_response = {
                    "checked_message": "사업자주소를 채워주세요!",
                }
                # return make_response(jsonify(data_response))
            elif not main_phonenumber:
                data_response = {
                    "checked_message": "대표전화번호를 채워주세요!",
                }
                # return make_response(jsonify(data_response))
            elif not main_cellphone:
                data_response = {
                    "checked_message": "사업자휴대폰번호를 채워주세요!",
                }
            return make_response(jsonify(data_response))

        else:
            abort(401)


@profiles_bp.route('/profile/existing/check/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def existing_profile_check_ajax(_id):
    """닉네임과 상호명을 체크하는 ajax"""
    profile = db.session.query(Profile).filter_by(id=_id).first()
    nickname = request.form.get("nickname")
    print(nickname)
    corp_brand = request.form.get("corp_brand")
    print(corp_brand)
    if nickname:
        existing_nickname = Profile.query.filter_by(nickname=nickname).first()
        if existing_nickname and (nickname != profile.nickname):
            # flash("동일한 닉네임이 존재합니다.")
            nickname_data_response = {
                "flash_message": "동일한 닉네임이 존재합니다.",
            }
        elif existing_nickname and (nickname == profile.nickname):
            nickname_data_response = {
                "flash_message": "닉네임이 그전과 동일해요. (사용가능)",
            }
        else:
            # flash("사용가능한 닉네임입니다.")
            print("else========================")
            nickname_data_response = {
                "flash_message": "사용가능한 닉네임입니다.",
            }
        return make_response(jsonify(nickname_data_response))
    if corp_brand:
        existing_corp_brand = Profile.query.filter_by(corp_brand=corp_brand).first()
        if existing_corp_brand and (corp_brand != profile.corp_brand):
            # flash("동일한 상호명이 존재합니다.")
            brand_data_response = {
                "flash_message": "동일한 상호명이 존재합니다.",
            }
        elif existing_corp_brand and (corp_brand == profile.corp_brand):
            brand_data_response = {
                "flash_message": "상호명이 그전과 동일해요. (사용가능)",
            }
        else:
            # flash("사용가능한 상호명입니다.")
            brand_data_response = {
                "flash_message": "사용가능한 상호명입니다.",
            }
        return make_response(jsonify(brand_data_response))
    # if not nickname:
    #     data_response = {
    #         "flash_message_nickname": "닉네임을 작성하고 중복체크바랍니다.",
    #     }
    #     return make_response(jsonify(data_response))
    # if not corp_brand:
    #     data_response = {
    #         "flash_message_corp_brand": "상호명을 작성하고 중복체크바랍니다.",
    #     }
    #     return make_response(jsonify(data_response))


@profiles_bp.route('/profile/vendor/delete/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_delete_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    if request.method == 'POST':
        if profile:
            if profile.level != "일반이용자":
                profile.level = "일반이용자"
            profile.corp_brand = ""
            profile.corp_email = ""
            profile.corp_number = ""
            profile.corp_online_marketing_number = ""
            if profile.corp_image_path:
                corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                if os.path.isfile(corp_image_origin_path):
                    shutil.rmtree(os.path.dirname(corp_image_origin_path))
            profile.corp_image_path = ""

            profile.corp_address = ""
            profile.main_phonenumber = ""
            profile.main_cellphone = ""
            db.session.add(profile)
            db.session.commit()

            data_response = {}
            return make_response(jsonify(data_response))
        else:
            abort(401)


@profiles_bp.route('/profile_cover_images/save/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def account_cover_img_save_ajax(_id):
    ajax_post_key()
    post_key = session["ajax_post_key"]  # 존재이유:게시판을 통하지 않고... 무작정 들어와서 이미지 올리는 것 막을려고....

    profile = db.session.query(Profile).filter_by(id=_id).first()
    user_id = profile.user_id
    existing_cover_img = db.session.query(ProfileCoverImage).filter_by(profile_id=profile.id).first()
    cover_img1 = request.files.get('cover_img1')
    cover_img2 = request.files.get('cover_img2')
    cover_img3 = request.files.get('cover_img3')
    if post_key and request.method == 'POST':
        if existing_cover_img:
            if cover_img1:
                relative_path1, upload_path1 = save_file(NOW, cover_img1)
                old_image_1_path = os.path.join(BASE_DIR, existing_cover_img.image_1_path)
                if old_image_1_path != upload_path1:
                    if os.path.isfile(old_image_1_path):
                        shutil.rmtree(os.path.dirname(old_image_1_path))
                existing_cover_img.image_1_path = relative_path1
            if cover_img2:
                relative_path2, upload_path2 = save_file(NOW, cover_img2)
                old_image_2_path = os.path.join(BASE_DIR, existing_cover_img.image_2_path)
                if old_image_2_path != upload_path2:
                    if os.path.isfile(old_image_2_path):
                        shutil.rmtree(os.path.dirname(old_image_2_path))
                existing_cover_img.image_2_path = relative_path2
            if cover_img3:
                relative_path3, upload_path3 = save_file(NOW, cover_img3)
                old_image_3_path = os.path.join(BASE_DIR, existing_cover_img.image_3_path)
                if old_image_3_path != upload_path3:
                    if os.path.isfile(old_image_3_path):
                        shutil.rmtree(os.path.dirname(old_image_3_path))
                existing_cover_img.image_3_path = relative_path3

            db.session.add(existing_cover_img)
            db.session.commit()
            session.pop('ajax_post_key', None)
            data_response = {
                "image_1_path": existing_cover_img.image_1_path,
                "image_2_path": existing_cover_img.image_2_path,
                "image_3_path": existing_cover_img.image_3_path,
            }
            return make_response(jsonify(data_response))

        else:
            new_cover_image = ProfileCoverImage()
            new_cover_image.user_id = user_id
            new_cover_image.profile_id = profile.id
            if cover_img1:
                relative_path1, _ = save_file(NOW, cover_img1)
                new_cover_image.image_1_path = relative_path1
            if cover_img2:
                relative_path2, _ = save_file(NOW, cover_img2)
                new_cover_image.image_2_path = relative_path2
            if cover_img3:
                relative_path3, _ = save_file(NOW, cover_img3)
                new_cover_image.image_3_path = relative_path3

            db.session.add(new_cover_image)
            db.session.commit()
            session.pop('ajax_post_key', None)
            data_response = {
                "image_1_path": new_cover_image.image_1_path,
                "image_2_path": new_cover_image.image_2_path,
                "image_3_path": new_cover_image.image_3_path,
            }
            return make_response(jsonify(data_response))
    else:
        return make_response(jsonify({"cover_img": 'else error'}))


@profiles_bp.route('/profile_cover_images/delete/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def account_cover_img_delete_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    existing_cover_img = db.session.query(ProfileCoverImage).filter_by(profile_id=profile.id).first()
    if request.method == 'POST':
        if profile and existing_cover_img:
            try:
                old_image_1_path = os.path.join(BASE_DIR, existing_cover_img.image_1_path)
                if os.path.isfile(old_image_1_path):
                    shutil.rmtree(os.path.dirname(old_image_1_path))
                old_image_2_path = os.path.join(BASE_DIR, existing_cover_img.image_2_path)
                if os.path.isfile(old_image_2_path):
                    shutil.rmtree(os.path.dirname(old_image_2_path))
                old_image_3_path = os.path.join(BASE_DIR, existing_cover_img.image_3_path)
                if os.path.isfile(old_image_3_path):
                    shutil.rmtree(os.path.dirname(old_image_3_path))
            except Exception as e:
                print(e)
        db.session.delete(existing_cover_img)
        db.session.commit()
        data_response = {
            "none_image_path": "/static/statics/images/none-image.png"
        }
        return make_response(jsonify(data_response))
    abort(401)


@profiles_bp.route('/profile/delete/ajax/<int:_id>', methods=['GET', 'POST'])
@profile_ownership_required
def delete_ajax(_id):
    """image_path and corp_image_path, cover_image_path 둘다 삭제해야 한다. profile_delete(profile)"""
    profile = db.session.query(Profile).filter_by(id=_id).one()
    user = db.session.query(User).filter_by(id=profile.user_id).one()
    if request.method == 'POST':
        if profile:
            profile_delete(profile)
            db.session.commit()
            data_response = {
                "account_dashboard_url": url_for('accounts.dashboard', _id=user.id)
            }
            return make_response(jsonify(data_response))
        abort(401)
