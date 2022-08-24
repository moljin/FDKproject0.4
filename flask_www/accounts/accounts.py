import os
import re
import shutil

from flask import render_template, Blueprint, session, redirect, url_for, g, flash, request
from flask_login import logout_user, current_user, login_user
from itsdangerous import SignatureExpired
from werkzeug import security

from flask_www.accounts.forms import LoginForm, AccountRegisterForm, AccountsUpdateForm, PasswordUpdateForm
from flask_www.accounts.models import User, Profile
from flask_www.accounts.utils import login_required, send_mail_for_any
from flask_www.commons.ownership_required import account_ownership_required
from flask_www.commons.utils import flash_form_errors
from flask_www.configs import db
from flask_www.configs.config import BASE_DIR

NAME = 'accounts'
accounts_bp = Blueprint(NAME, __name__, url_prefix='/accounts')


@accounts_bp.before_app_request
def before_app_request():
    g.user = None
    email = session.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            g.user = user
        else:
            session.pop('email', None)


@accounts_bp.route('/', methods=['GET'])  # /accounts로 진입하면 로그인 페이지로 보낸다.
def index():
    try:
        user_id = current_user.id
        profile = Profile.query.filter_by(user_id=user_id).one()
    except:
        profile = None
    return redirect(url_for(f'{NAME}.login', profile=profile))


@accounts_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('accounts/dashboard/dashboard_index.html')


@accounts_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = AccountRegisterForm()
    email = form.email.data
    existing_email_user = User.query.filter_by(email=email).first()
    password_reg = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{9,30}$"
    regex = re.compile(password_reg)
    password_reg_mat = re.search(regex, str(form.password.data))
    try:
        if existing_email_user:
            flash("가입된 이메일이 존재합니다.")
        elif form.validate_on_submit():
            if not password_reg_mat:
                flash('비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.')
                return redirect(request.path)
            hashed_password = security.generate_password_hash(form.password.data)
            new_user = User(
                email=request.form.get('email'),
                password=hashed_password,
            )
            from flask_www.configs import safe_time_serializer
            auth_token = safe_time_serializer.dumps(email, salt='email-confirm')
            new_user.auth_token = auth_token
            db.session.add(new_user)
            db.session.commit()

            subject = "β-0.0.2 회원등록 인증용 메일"
            msg_txt = 'accounts/send_mails/account_update_register_mail.txt'
            msg_html = 'accounts/send_mails/account_update_register_mail.html'
            send_mail_for_any(subject, email, auth_token, msg_txt, msg_html)
            return redirect(url_for('accounts.token_send', email=email))  # 이렇게 token_send로 이메일을 넘겨 줄수도 있다.
        else:
            flash_form_errors(form)

    except Exception as e:
        print(e)
    return render_template("accounts/users/register.html", form=form)


@accounts_bp.route('/verification/token/send/<email>', methods=['GET'])
def token_send(email):
    return render_template("accounts/users/etc/token_send.html", email=email)


@accounts_bp.route('/confirm-email/<token>')
def confirm_email(token):
    try:
        from flask_www.configs import safe_time_serializer
        email = safe_time_serializer.loads(token, salt='email-confirm', max_age=86400)  # 24시간 cf. 60 == 60초 즉, 1분
        user_obj = User.query.filter_by(email=email).first()
        password_confirm = 'password_confirm'

        if user_obj and user_obj.is_verified and not password_confirm:
            flash('이메일 인증이 이미 되어 있어요!')
            return redirect(url_for('accounts.login'))
        elif user_obj and not user_obj.is_verified:
            user_obj.is_verified = True
            db.session.commit()
            flash('이메일 인증이 완료되었습니다.')
            return redirect(url_for('accounts.login'))
        elif user_obj and password_confirm:
            session['password_token'] = token
            return redirect(url_for('accounts.forget_password_update', _id=user_obj.id, password_token=token))
        else:
            flash('가입한 내용이 없거나 . . . 문제가 발생했습니다.')
    except SignatureExpired:
        confirm_expired_msg = '토큰이 죽었어요...!'
        return confirm_expired_msg
    return redirect(url_for('accounts.register'))  # 가입도 안된 토큰으로 시도할 때 flash를 안고 돌아간다.... #'<h1>토큰이 살아 있어요....</h1>'  # True 로 바꿔주고, 링크를 클릭하면 인증완료된다.


@accounts_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash("로그인 상태입니다!")
        return redirect(url_for("commons.index"))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('등록된 이메일이 없어요!')
            return redirect(url_for('accounts.register'))
        elif user and not user.is_verified:
            flash('이메일 인증이 되지 않았습니다. 메일을 확인하세요.')
            return redirect(url_for('accounts.login'))
        elif user and user.is_verified:
            if security.check_password_hash(user.password, form.password.data):
                login_user(user)
                session['email'] = user.email  # 추가
                path_redirect = request.args.get("next")  # .split('?next=/')  # get the original page
                if path_redirect:
                    return redirect(url_for('/' + path_redirect))
                else:
                    return redirect(url_for('accounts.dashboard'))  # redirect('/')
            else:
                flash("비밀번호를 확인하세요 . . . ")
        else:
            flash('이메일을 확인하거나 가입후 이용하세요!!')
    else:
        flash_form_errors(form)
    return render_template('accounts/users/login.html', form=form)


@accounts_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('email', None)
    logout_user()
    return redirect(url_for('accounts.login'))


@accounts_bp.route('/update/<int:_id>', methods=['GET', 'POST'])
@account_ownership_required
def email_update(_id):
    form = AccountsUpdateForm()
    user = User.query.get_or_404(_id)
    new_email = form.email.data
    if form.validate_on_submit():
        if new_email != user.email:
            user.email = new_email
            from flask_www.configs import safe_time_serializer
            auth_token = safe_time_serializer.dumps(new_email, salt='email-confirm')
            user.auth_token = auth_token
            user.is_verified = False
            db.session.commit()

            subject = "β-0.0.5 메일 수정 인증용 메일"
            msg_txt = 'accounts/send_mails/account_register_mail.txt'
            msg_html = 'accounts/send_mails/account_register_mail.html'
            # send_mail_for_verification(new_email, auth_token, msg_txt, msg_html)
            send_mail_for_any(subject, new_email, auth_token, msg_txt, msg_html)
            # 이미 session.get('email')까지 None 으로 됐기 때문에 session.pop('email', None)은 필요없다.
            logout_user()
            return redirect(url_for('accounts.token_send', email=new_email))
        else:
            flash('가입된 이메일과 동일해요 . . . ')
    return render_template('accounts/resetting/email_update.html', user=user, form=form)


@accounts_bp.route('/password/update/<int:_id>', methods=['GET', 'POST'])
@account_ownership_required
def password_update(_id):
    form = PasswordUpdateForm()
    user_obj = User.query.get_or_404(_id)
    password_reg = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{9,30}$"
    regex = re.compile(password_reg)
    password_reg_mat = re.search(regex, str(form.password.data))
    if not user_obj:
        flash('가입된 회원이 아니에요 . . .')
    elif form.validate_on_submit():
        if not password_reg_mat:
            flash('비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.')
            return redirect(request.path)
        hashed_password = security.generate_password_hash(form.password.data)
        user_obj.password = hashed_password
        db.session.commit()
        logout_user()
        flash('비밀번호가 변경되었어요. . .')
        return redirect(url_for('accounts.login'))
    else:
        flash_form_errors(form)
    return render_template('accounts/resetting/password_update.html', user=user_obj, form=form)


@accounts_bp.route('forget/password', methods=['GET', 'POST'])
def forget_password_email():
    form = AccountsUpdateForm()
    email = form.email.data

    if form.validate_on_submit():
        user_obj = User.query.filter_by(email=email).first()
        if user_obj:
            from flask_www.configs import safe_time_serializer
            password_token = safe_time_serializer.dumps(email, salt='email-confirm')
            user_obj.password_token = password_token
            db.session.commit()

            subject = "β-0.0.2 비밀번호 변경 인증용 메일"
            msg_txt = 'accounts/send_mails/account_update_register_mail.txt'
            msg_html = 'accounts/send_mails/account_update_register_mail.html'
            send_mail_for_any(subject, email, password_token, msg_txt, msg_html)
            # send_mail_for_password_verification(email, password_token)
            flash('이메일을 전송하였습니다. 메일을 확인하세요')
            return redirect(url_for('accounts.token_send', email=email))
        else:
            flash('등록된 이메일이 없어요!')
            return redirect(url_for('accounts.register', form=AccountRegisterForm()))

    return render_template('accounts/resetting/forget_pw_email.html', form=form)


@accounts_bp.route('password/confirm-email/<password_token>')
def forget_password_confirm_email(password_token):  # confirm_email 에 통합 함
    try:
        from flask_www.configs import safe_time_serializer
        email = safe_time_serializer.loads(password_token, salt='email-confirm', max_age=86400)  # 24시간 cf. 60 == 60초 즉, 1분
        user_obj = User.query.filter_by(email=email).first()

        if user_obj:
            session['password_token'] = password_token
            return redirect(url_for('accounts.forget_password_update', pk_id=user_obj.id, password_token=password_token))
        else:
            flash('가입한 내용이 없거나 . . . 문제가 발생했습니다.')
    except SignatureExpired:
        confirm_expired_msg = '토큰이 죽었어요...!'
        return redirect(url_for('accounts.register', message=confirm_expired_msg))
    return redirect(url_for('accounts.register'))  # 가입도 안된 토큰으로 시도할 때 flash를 안고 돌아간다.... #'<h1>토큰이 살아 있어요....</h1>'  # True 로 바꿔주고, 링크를 클릭하면 인증완료된다.


@accounts_bp.route('/pwforget/update/<int:_id>/<password_token>', methods=['GET', 'POST'])
def forget_password_update(_id, password_token):
    form = PasswordUpdateForm()
    user_obj = User.query.get_or_404(_id)
    password_reg = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{9,30}$"
    regex = re.compile(password_reg)
    password_reg_mat = re.search(regex, str(form.password.data))
    try:
        if session['password_token']:
            if form.validate_on_submit():
                if not password_reg_mat:
                    flash('비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.')
                    return redirect(request.path)
                hashed_password = security.generate_password_hash(form.password.data)
                user_obj.password = hashed_password
                user_obj.password_token = password_token
                db.session.commit()
                return redirect(url_for('accounts.login'))
            else:
                flash_form_errors(form)
        else:
            print('444444444444444444444444')
            message = '잘못된 접근입니다 . . .'
            # flash('잘못된 접근입니다 . . .')
            return redirect(url_for('accounts.athentication_error', message=message))
    except Exception as e:
        print(e)
        message = '무작정 들어온.... 잘못된 접근입니다 . . .'
        return redirect(url_for('accounts.athentication_error', message=message))
    return render_template('accounts/resetting/forget_pw_update.html', user=user_obj, form=form)


@accounts_bp.route('/delete/<_id>', methods=['POST', 'GET'])#
@account_ownership_required
def delete(_id):
    if request.method == 'POST': # 이거는 꼭 없어도 된다.
        # _id = request.form.get('_id')
        print('999999999999999999999999', _id)
        # user_obj = User.query.filter(User.id == _id)
        user_obj = db.session.query(User).filter_by(id=_id).first()
        profile = db.session.query(Profile).filter_by(user_id=_id).first()
        if profile:
            try:
                profile_image_origin_path = os.path.join(BASE_DIR, profile.image_path)
                if os.path.isfile(profile_image_origin_path):
                    shutil.rmtree(os.path.dirname(profile_image_origin_path))
                corp_image_origin_path = os.path.join(BASE_DIR, profile.corp_image_path)
                if os.path.isfile(corp_image_origin_path):
                    shutil.rmtree(os.path.dirname(corp_image_origin_path))
            except Exception as e:
                print(e)
            db.session.delete(profile)
            # db.session.commit()
        # user_obj.delete()
        db.session.delete(user_obj)
        db.session.commit()
        return redirect(url_for('commons.index'))


@accounts_bp.route('accounts/error')
def athentication_error():
    return render_template('accounts/users/etc/error.html')
