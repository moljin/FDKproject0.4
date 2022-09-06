from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField, IntegerField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Length

from flask_www.ecomm.products.models import ShopCategory


class ShopCategoryForm(FlaskForm):
    title = StringField("상점 타이틀", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "상점 타이틀"})
    content = TextAreaField("간단한 소개글", validators=[DataRequired()], render_kw={"placeholder": "간단한 소개글"})
    meta_description = TextAreaField("메타설명", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "메타 설명"})
    # symbol_image = FileField("브랜드 심볼", validators=[DataRequired()])


class OptionForm(FlaskForm):
    op_category = StringField("옵션 카테고리", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "옵션 카테고리"})
    op_title = StringField("타이틀", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "타이틀"})

    op_price = IntegerField("가격", validators=[DataRequired()], render_kw={"placeholder": "가격"})
    op_stock = IntegerField("재고", validators=[DataRequired()], render_kw={"placeholder": "재고"})

    op_available_display = BooleanField("전시여부", default=True)


class ProductForm(FlaskForm):
    title = StringField("타이틀", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "타이틀"})
    shopcategory = SelectField("점빵 카테고리")
    content = TextAreaField("내용", validators=[DataRequired()], render_kw={"placeholder": "내용"})
    meta_description = TextAreaField("메타설명", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "메타 설명"})
    linked_image = FileField("이미지", validators=[DataRequired()], render_kw={"placeholder": "이미지"})

    price = IntegerField("가격", validators=[DataRequired()], render_kw={"placeholder": "가격"})
    stock = IntegerField("재고", validators=[DataRequired()], render_kw={"placeholder": "재고"})
    base_dc_amount = IntegerField("기본 할인금액", default=0, render_kw={"placeholder": "기본 할인금액"})
    delivery_pay = IntegerField("배송비", default=0, render_kw={"placeholder": "배송비"})

    available_display = BooleanField("전시여부", default=True)
    available_order = BooleanField("주문가능", default=True)

    option_field = FieldList(FormField(OptionForm), min_entries=2)  # https://www.youtube.com/watch?v=K2czdygI2wM

    def __init__(self):
        super(ProductForm, self).__init__()
        user_pc_list = [(pc.id, pc.title) for pc in ShopCategory.query.filter_by(user_id=current_user.id)]
        self.shopcategory.choices = user_pc_list


