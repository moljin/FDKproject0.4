from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length, EqualTo, DataRequired


class AccountRegisterForm(FlaskForm):  # render_kw={"placeholder": "이메일"}::: 템플릿단의 설정이 먼저 적용된다.
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=120)], render_kw={"placeholder": "이메일"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=9, max=20), EqualTo('repassword', message='입력한 비밀번호가 서로 달라요 . . .')], render_kw={"placeholder": "비밀번호"})
    repassword = PasswordField('repassword', validators=[InputRequired(), Length(min=9, max=20)], render_kw={"placeholder": "비밀번호 확인"})
    submit = SubmitField("가입하기")


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=120)], render_kw={"placeholder": "이메일"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "비밀번호"})


class ProfileForm(FlaskForm):
    nickname = StringField("닉네임", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "닉네임"})
    message = TextAreaField("메시지", validators=[DataRequired()], render_kw={"placeholder": "간단 메시지"})
    # profile_image = FileField("프로필 이미지", validators=[DataRequired()], render_kw={"placeholder": "프로필 이미지"})


class AccountsUpdateForm(FlaskForm):
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=120)], render_kw={"placeholder": "이메일"})


class PasswordUpdateForm(FlaskForm):
    password = PasswordField('password', validators=[InputRequired(), Length(min=9, max=20), EqualTo('repassword', message='입력한 비밀번호가 서로 달라요 . . .')], render_kw={"placeholder": "비밀번호"})
    repassword = PasswordField('repassword', validators=[InputRequired(), Length(min=9, max=20)], render_kw={"placeholder": "비밀번호 확인"})


class VendorForm(ProfileForm):
    nickname = StringField("닉네임", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "닉네임"})
    message = TextAreaField("메시지", validators=[DataRequired()], render_kw={"placeholder": "간단 메시지"})
    profile_image = FileField("프로필 이미지", validators=[DataRequired()], render_kw={"placeholder": "프로필 이미지"})
    corp_email = StringField("사업자용 이메일", validators=[DataRequired(), Length(min=5, max=120)], render_kw={"placeholder": "사업자용 이메일"})
    corp_number = StringField("사업자 등록번호", validators=[DataRequired()], render_kw={"placeholder": "사업자 등록번호"})
    corp_image = FileField("사업자 등록증", validators=[DataRequired()], render_kw={"placeholder": "사업자 등록증"})
    corp_address = StringField("사업자 주소", validators=[DataRequired()], render_kw={"placeholder": "사업자 주소"})
    main_phonenumber = StringField("대표 전화번호", validators=[DataRequired()], render_kw={"placeholder": "대표 전화번호"})
    main_cellphone = StringField("사업자 휴대폰", validators=[DataRequired()], render_kw={"placeholder": "사업자 휴대폰"})


class VendorAjaxForm(ProfileForm):
    corp_email = StringField("사업자용 이메일", validators=[DataRequired(), Length(min=5, max=120)], render_kw={"placeholder": "사업자용 이메일"})
    corp_number = StringField("사업자 등록번호", validators=[DataRequired()], render_kw={"placeholder": "사업자 등록번호"})
    corp_image = FileField("사업자 등록증", validators=[DataRequired()], render_kw={"placeholder": "사업자 등록증"})
    corp_address = StringField("사업자 주소", validators=[DataRequired()], render_kw={"placeholder": "사업자 주소"})
    main_phonenumber = StringField("대표 전화번호", validators=[DataRequired()], render_kw={"placeholder": "대표 전화번호"})
    main_cellphone = StringField("사업자 휴대폰", validators=[DataRequired()], render_kw={"placeholder": "사업자 휴대폰"})