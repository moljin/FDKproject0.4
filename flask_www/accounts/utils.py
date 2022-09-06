import os
import shutil

from flask import url_for, render_template, flash, redirect, request, session, abort
from flask_mail import Message
from flask_login import current_user
from functools import wraps

from flask_www.accounts.models import User, Profile, ProfileCoverImage
from flask_www.configs import mail, db
from flask_www.configs.config import Config, BASE_DIR


def admin_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        if current_user.is_authenticated:
            if not current_user.is_admin:
                abort(401)
        else:
            abort(401)
        return function(*args, **kwargs)
    return decorator_function


def login_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        if not current_user.is_authenticated:
            try:
                session['previous_url'] = request.form.get('next')
            except:
                session['previous_url'] = None
            return redirect(url_for('accounts.login'))
        return function(*args, **kwargs)
    return decorator_function


def vendor_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        try:
            logged_user_email = session['email']
            user_obj = User.query.filter_by(email=logged_user_email).first()
            profile_obj = Profile.query.filter_by(user_id=user_obj.id).first()
            if profile_obj.level != '판매사업자':
                return redirect(url_for('profiles.vendor_not'))
            return function(*args, **kwargs)
        except Exception as e:
            print(e)
            flash('로그인이나 회원가입후에 가능해요.')
            return redirect(url_for('accounts.login'))
    return decorator_function


def send_mail_for_any(subject, email, token, msg_txt, msg_html):
    """통합: 회원등록 인증메일, 비밀번호 분실시 재설정 인증메일, vendor update 알림메일"""
    msg = Message(subject, sender=Config().MAIL_USERNAME, recipients=[email])
    add_if = "템플릿단에서 조건을 추가하고자 할 때... 이게 False 이면 회원등록완료하기 html 을 준다."
    try:
        link = url_for('accounts.confirm_email', token=token, _external=True)
    except Exception as e:
        print(e)
        link = None
    msg.body = render_template(msg_txt)
    msg.html = render_template(msg_html, link=link, email=email, add_if=add_if)
    mail.send(msg)

    return True


def profile_delete(profile):
    try:
        profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
        if os.path.isfile(profile_image_origin_path):
            shutil.rmtree(os.path.dirname(profile_image_origin_path))
        if profile.corp_image_path:
            corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
            if os.path.isfile(corp_image_origin_path):
                shutil.rmtree(os.path.dirname(corp_image_origin_path))
        existing_cover_img = db.session.query(ProfileCoverImage).filter_by(profile_id=profile.id).first()
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
