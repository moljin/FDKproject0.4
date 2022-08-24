import os
import shutil

from flask import Blueprint, g, redirect, url_for, render_template, request, abort, session, make_response, jsonify
from flask_login import current_user

from flask_www.accounts.forms import ProfileForm, VendorForm, VendorAjaxForm
from flask_www.accounts.models import Profile, User, LEVELS, ProfileCoverImage
from flask_www.accounts.utils import login_required, send_mail_for_any
from flask_www.commons.ownership_required import profile_ownership_required
from flask_www.commons.utils import save_file, ajax_post_key
from flask_www.configs import db
from flask_www.configs.config import NOW, BASE_DIR

NAME = 'profiles'
profiles_bp = Blueprint(NAME, __name__, url_prefix='/accounts')


@profiles_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProfileForm()
    nickname = form.nickname.data
    message = form.message.data
    profile_image = form.data.get('profile_image')
    print(profile_image)
    # profile_image = request.files.get('profile_image')
    if form.validate_on_submit():
        new_profile = Profile(
            nickname=nickname,
            message=message,
            user_id=g.user.id
        )
        if profile_image:
            relative_path, _ = save_file(NOW, profile_image)
            new_profile.image_path = relative_path
            print(new_profile.image_path)
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for('profiles.detail', _id=new_profile.id))
    # else:
    #     flash('이미 등록한 닉네임이 있습니다.')
    return render_template('accounts/profiles/profile_create.html', form=form)


@profiles_bp.route('/profile/detail/<int:_id>', methods=['GET'])
def detail(_id):
    profile_obj = db.session.query(Profile).filter_by(id=_id).first()
    user_id = profile_obj.user_id
    user_obj = User.query.get_or_404(user_id)
    cover_img_obj = db.session.query(ProfileCoverImage).filter_by(profile_id=profile_obj.id).first()
    return render_template('accounts/profiles/profile_detail.html', target_profile_user=user_obj, target_profile=profile_obj, cover_img=cover_img_obj)


@profiles_bp.route('/profile/vendor/not', methods=['GET', 'POST'])
@login_required
def vendor_not():
    _id = current_user.id
    user_obj = User.query.get_or_404(_id)
    profile_obj = Profile.query.filter_by(user_id=user_obj.id).first()
    return render_template('accounts/profiles/vendor_not.html', user=user_obj, profile=profile_obj)


@profiles_bp.route('/profile/update/<int:_id>', methods=['GET', 'POST'])
@profile_ownership_required
def update(_id):
    form = ProfileForm(request.form)
    profile = db.session.query(Profile).filter_by(id=_id).one()
    if request.method == 'POST':
        if profile:
            print("1: ", form.data.get("message"))
            print("2: ",request.form.get("message"))
            profile.nickname = form.data.get("nickname")
            profile.message = form.data.get("message")
            # profile_image = form.data.get('profile_image')
            profile_image = request.files.get('profile_image')
            if profile_image:
                profile_image_relative_path, profile_image_upload_path = save_file(NOW, profile_image)
                if profile.image_path:
                    profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
                    if profile_image_origin_path != profile_image_upload_path:
                        if os.path.isfile(profile_image_origin_path):
                            shutil.rmtree(os.path.dirname(profile_image_origin_path))
                profile.image_path = profile_image_relative_path
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for('profiles.detail', _id=_id))
    return render_template('accounts/profiles/profile_update.html', form=form, getprofile=profile)


@profiles_bp.route('/profile/update/ajax/<int:_id>', methods=['GET', 'POST'])
@profile_ownership_required
def update_ajax(_id):
    user_id = current_user.id
    profile = db.session.query(Profile).filter_by(user_id=user_id).one()
    if request.method == 'POST':
        if profile:
            profile.nickname = request.form.get("nickname")
            profile.message = request.form.get("message")
            profile_image = request.files.get('profile_image')
            if profile_image:
                profile_image_relative_path, profile_image_upload_path = save_file(NOW, profile_image)
                if profile.image_path:
                    profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
                    if profile_image_origin_path != profile_image_upload_path:
                        if os.path.isfile(profile_image_origin_path):
                            shutil.rmtree(os.path.dirname(profile_image_origin_path))
                profile.image_path = profile_image_relative_path
            db.session.add(profile)
            db.session.commit()

            data_response = {
                "profile_nickname": profile.nickname,
                "profile_message": profile.message,
                "profile_image_path": profile.image_path,
            }
            return make_response(jsonify(data_response))
        else:
            abort(401)


@profiles_bp.route('profile/vendor/detail/<int:_id>', methods=['GET'])
@login_required
def vendor_detail(_id):
    profile_obj = db.session.query(Profile).filter_by(id=_id).first()
    user_obj = db.session.query(User).filter_by(id=profile_obj.user_id).first()
    cover_img_obj = db.session.query(ProfileCoverImage).filter_by(profile_id=profile_obj.id).first()
    return render_template('accounts/profiles/profile_detail.html', target_profile_user=user_obj, target_profile=profile_obj, cover_img=cover_img_obj)


@profiles_bp.route('profile/vendor/update/<int:_id>', methods=['GET', 'POST'])
@profile_ownership_required
def vendor_update(_id):
    form = VendorAjaxForm(request.form)
    profile = db.session.query(Profile).filter_by(id=_id).one()
    level = profile.nickname + '[' + profile.level + ']' + ':vendor-register'
    print("level", level)
    if request.method == 'POST':
        if profile:
            profile.nickname = form.data.get("nickname")
            profile.message = form.data.get("message")
            req_level = request.form.get('level')
            print("req_level", req_level)
            if req_level == level:
                if profile.level == "일반이용자":
                    profile.level = LEVELS[1]
            # profile_image = form.data.get('profile_image')
            profile_image = request.files.get('profile_image')
            if profile_image:
                profile_image_relative_path, profile_image_upload_path = save_file(NOW, profile_image)
                if profile.image_path:
                    profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
                    if profile_image_origin_path != profile_image_upload_path:
                        if os.path.isfile(profile_image_origin_path):
                            shutil.rmtree(os.path.dirname(profile_image_origin_path))
                profile.image_path = profile_image_relative_path

            profile.corp_email = form.data.get("corp_email")
            profile.corp_number = form.data.get("corp_number")

            corp_image = request.files.get('corp_image')
            if corp_image:
                corp_image_relative_path, corp_image_upload_path = save_file(NOW, corp_image)
                if profile.corp_image_path:
                    corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                    if corp_image_origin_path != corp_image_upload_path:
                        if os.path.isfile(corp_image_origin_path):
                            shutil.rmtree(os.path.dirname(corp_image_origin_path))
                profile.corp_image_path = corp_image_relative_path

            profile.corp_address = form.data.get("corp_address")
            profile.main_phonenumber = form.data.get("main_phonenumber")
            profile.main_cellphone = form.data.get("main_cellphone")
            db.session.add(profile)
            db.session.commit()

            subject = "판매사업자 신청 메일"
            user_email = current_user.email
            token = None
            msg_txt = 'accounts/send_mails/account_update_register_mail.txt'
            msg_html = 'accounts/send_mails/account_update_register_mail.html'
            send_mail_for_any(subject, user_email, token, msg_txt, msg_html)
            return redirect(url_for('profiles.vendor_detail', _id=_id))
    return render_template('accounts/profiles/vendor_update.html', form=form, getprofile=profile, level=level)


@profiles_bp.route('/profile/vendor/update/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_update_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    level = profile.level
    if request.method == 'POST':
        if profile:
            req_level = request.form.get('level')
            if req_level == level:
                if profile.level == "일반이용자":
                    profile.level = LEVELS[1]

            profile.corp_email = request.form.get("corp_email")
            profile.corp_number = request.form.get("corp_number")

            corp_image = request.files.get('corp_image')
            if corp_image:
                corp_image_relative_path, corp_image_upload_path = save_file(NOW, corp_image)
                if profile.corp_image_path:
                    corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                    if corp_image_origin_path != corp_image_upload_path:
                        if os.path.isfile(corp_image_origin_path):
                            shutil.rmtree(os.path.dirname(corp_image_origin_path))
                profile.corp_image_path = corp_image_relative_path

            profile.corp_address = request.form.get("corp_address")
            profile.main_phonenumber = request.form.get("main_phonenumber")
            profile.main_cellphone = request.form.get("main_cellphone")
            db.session.add(profile)
            db.session.commit()

            subject = "판매사업자 신청 메일"
            user_email = current_user.email
            token = None
            msg_txt = 'accounts/send_mails/account_update_register_mail.txt'
            msg_html = 'accounts/send_mails/account_update_register_mail.html'
            send_mail_for_any(subject, user_email, token, msg_txt, msg_html)

            data_response = {
                "corp_email": profile.corp_email,
                "corp_number": profile.corp_number,
                "corp_image_path": profile.corp_image_path,
                "corp_address": profile.corp_address,
                "main_phonenumber": profile.main_phonenumber,
                "main_cellphone": profile.main_cellphone,
                "profile_level": profile.level
            }
            return make_response(jsonify(data_response))
        else:
            abort(401)


@profiles_bp.route('/profile/vendor/delete/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_delete_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    if request.method == 'POST':
        if profile:
            if profile.level != "일반이용자":
                profile.level = "일반이용자"
            profile.corp_email = ""
            profile.corp_number = ""
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


@profiles_bp.route('/profile/delete/<int:_id>', methods=['GET', 'POST'])
@profile_ownership_required
def delete(_id):
    """image_path and corp_image_path 둘다 삭제해야 한다."""
    profile = db.session.query(Profile).filter_by(id=_id).one()
    user = db.session.query(User).filter_by(id=profile.user_id).one()
    existing_cover_img = db.session.query(ProfileCoverImage).filter_by(profile_id=profile.id).first()
    if request.method == 'POST':
        if profile:
            try:
                profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
                if os.path.isfile(profile_image_origin_path):
                    shutil.rmtree(os.path.dirname(profile_image_origin_path))
                corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                if os.path.isfile(corp_image_origin_path):
                    shutil.rmtree(os.path.dirname(corp_image_origin_path))
                if existing_cover_img:
                    old_image_1_path = os.path.join(BASE_DIR, existing_cover_img.image_1_path)
                    if os.path.isfile(old_image_1_path):
                        shutil.rmtree(os.path.dirname(old_image_1_path))
                    old_image_2_path = os.path.join(BASE_DIR, existing_cover_img.image_2_path)
                    if os.path.isfile(old_image_2_path):
                        shutil.rmtree(os.path.dirname(old_image_2_path))
                    old_image_3_path = os.path.join(BASE_DIR, existing_cover_img.image_3_path)
                    if os.path.isfile(old_image_3_path):
                        shutil.rmtree(os.path.dirname(old_image_3_path))
                db.session.delete(existing_cover_img)
            except Exception as e:
                print(e)
            db.session.delete(profile)
            db.session.commit()
            return redirect(url_for('accounts.resetting', _id=user.id))
        abort(404)

    return render_template('accounts/profiles/profile_delete.html', profile=profile)


@profiles_bp.route('/profile/delete/ajax/<int:_id>', methods=['GET', 'POST'])
@profile_ownership_required
def delete_ajax(_id):
    """image_path and corp_image_path 둘다 삭제해야 한다."""
    profile = db.session.query(Profile).filter_by(id=_id).one()
    user = db.session.query(User).filter_by(id=profile.user_id).one()
    existing_cover_img = db.session.query(ProfileCoverImage).filter_by(profile_id=profile.id).first()
    if request.method == 'POST':
        if profile:
            try:
                profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
                if os.path.isfile(profile_image_origin_path):
                    shutil.rmtree(os.path.dirname(profile_image_origin_path))
                corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                if os.path.isfile(corp_image_origin_path):
                    shutil.rmtree(os.path.dirname(corp_image_origin_path))
                if existing_cover_img:
                    old_image_1_path = os.path.join(BASE_DIR, existing_cover_img.image_1_path)
                    if os.path.isfile(old_image_1_path):
                        shutil.rmtree(os.path.dirname(old_image_1_path))
                    old_image_2_path = os.path.join(BASE_DIR, existing_cover_img.image_2_path)
                    if os.path.isfile(old_image_2_path):
                        shutil.rmtree(os.path.dirname(old_image_2_path))
                    old_image_3_path = os.path.join(BASE_DIR, existing_cover_img.image_3_path)
                    if os.path.isfile(old_image_3_path):
                        shutil.rmtree(os.path.dirname(old_image_3_path))
                db.session.delete(existing_cover_img)
            except Exception as e:
                print(e)
            db.session.delete(profile)
            db.session.commit()
            data_response = {
                "account_dashboard_url": url_for('accounts.dashboard', _id=user.id)
            }
            return make_response(jsonify(data_response))
        abort(401)
