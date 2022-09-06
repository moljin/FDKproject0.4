import os
import shutil
import uuid

from flask import Blueprint, render_template, flash, make_response, jsonify, redirect, url_for, g, session, request, abort
from flask_login import current_user
from sqlalchemy import desc

from flask_www.accounts.models import Profile, User
from flask_www.accounts.utils import login_required, vendor_required
from flask_www.commons.ownership_required import shopcategory_ownership_required, product_ownership_required
from flask_www.commons.utils import flash_form_errors, save_file, ajax_post_key, base64_to_file, c_slugify
from flask_www.configs import db
from flask_www.configs.config import NOW, BASE_DIR
from flask_www.ecomm.products.forms import ShopCategoryForm, ProductForm
from flask_www.ecomm.products.models import ShopCategory, ShopCategoryCoverImage, UnitsProductImage, Product

NAME = 'products'
products_bp = Blueprint(NAME, __name__, url_prefix='/products')


@products_bp.route('/shop-category/create', methods=['GET', 'POST'])
@vendor_required
def shopcategory_create():
    form = ShopCategoryForm()
    title = form.title.data
    existing_title = ShopCategory.query.filter_by(title=title).first()
    content = form.content.data
    meta_description = form.meta_description.data
    symbol_image = form.data.get('symbol_image')
    try:
        if existing_title:
            flash("등록된 상점타이틀이 존재합니다.")
        elif form.validate_on_submit():
            new_shopcategory = ShopCategory(
                user_id=g.user.id,
                title=title
            )
            new_shopcategory.content = content
            new_shopcategory.meta_description = meta_description

            # if symbol_image:
            #     relative_path, _ = save_file(NOW, symbol_image)
            #     new_shopcategory.symbol_path = relative_path
            db.session.add(new_shopcategory)
            db.session.commit()

            return redirect(url_for('products.shopcategory_detail', _id=new_shopcategory.id, slug=new_shopcategory.slug))
        else:
            flash_form_errors(form)

    except Exception as e:
        print(e)
    return render_template('ecomm/products/shopcategory_create.html', form=form)


@products_bp.route('/shopcategory_symbol_images/save/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def shopcategory_symbol_img_save_ajax(_id):
    ajax_post_key()
    post_key = session["ajax_post_key"]

    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).first()
    existing_symbol_img = shopcategory.symbol_path
    symbol_image = request.files.get('symbol_image')
    if post_key and request.method == 'POST':
        if existing_symbol_img:
            if symbol_image:
                relative_path, upload_path = save_file(NOW, symbol_image)
                old_symbol_path = os.path.join(BASE_DIR, existing_symbol_img)
                if old_symbol_path != upload_path:
                    if os.path.isfile(old_symbol_path):
                        shutil.rmtree(os.path.dirname(old_symbol_path))
                shopcategory.symbol_path = relative_path
        else:
            if symbol_image:
                relative_path, _ = save_file(NOW, symbol_image)
                shopcategory.symbol_path = relative_path
        db.session.add(shopcategory)
        db.session.commit()
        session.pop('ajax_post_key', None)
        shop_data_response = {
            "symbol_path": shopcategory.symbol_path,
        }
        return make_response(jsonify(shop_data_response))
    abort(401)


@products_bp.route('/shopcategory_symbol_images/delete/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def shopcategory_symbol_img_delete_ajax(_id):
    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).first()
    existing_symbol_img = shopcategory.symbol_path
    if request.method == 'POST':
        if existing_symbol_img:
            try:
                old_symbol_path = os.path.join(BASE_DIR, existing_symbol_img)
                if os.path.isfile(old_symbol_path):
                    shutil.rmtree(os.path.dirname(old_symbol_path))
                shopcategory.symbol_path = ""
            except Exception as e:
                print(e)
        db.session.add(shopcategory)
        db.session.commit()
        shop_data_response = {
            "symbol_path": "static/statics/images/sample_logo.png" # 맨앞 / 를 빼고 넘긴다. ...
        }
        return make_response(jsonify(shop_data_response))
    abort(401)


@products_bp.route('/shopcategory_cover_images/save/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def shopcategory_cover_img_save_ajax(_id):
    ajax_post_key()
    post_key = session["ajax_post_key"]  # 존재이유:게시판을 통하지 않고... 무작정 들어와서 이미지 올리는 것 막을려고....

    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).first()
    user_id = shopcategory.user_id
    existing_cover_img = db.session.query(ShopCategoryCoverImage).filter_by(shopcategory_id=shopcategory.id).first()
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
            shop_data_response = {
                "image_1_path": existing_cover_img.image_1_path,
                "image_2_path": existing_cover_img.image_2_path,
                "image_3_path": existing_cover_img.image_3_path,
            }
            return make_response(jsonify(shop_data_response))

        else:
            new_cover_image = ShopCategoryCoverImage()
            new_cover_image.user_id = user_id
            new_cover_image.shopcategory_id = shopcategory.id
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
            shop_data_response = {
                "image_1_path": new_cover_image.image_1_path,
                "image_2_path": new_cover_image.image_2_path,
                "image_3_path": new_cover_image.image_3_path,
            }
            return make_response(jsonify(shop_data_response))
    else:
        return make_response(jsonify({"cover_img": 'else error'}))


@products_bp.route('/shopcategory_cover_images/delete/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def shopcategory_cover_img_delete_ajax(_id):
    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).first()
    existing_cover_img = db.session.query(ShopCategoryCoverImage).filter_by(shopcategory_id=shopcategory.id).first()
    if request.method == 'POST':
        if shopcategory and existing_cover_img:
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
        shop_data_response = {
            "none_image_path": "/static/statics/images/shop-cover.jpg"
        }
        return make_response(jsonify(shop_data_response))
    abort(401)


@products_bp.route('/shop-category/detail/<int:_id>/<slug>', methods=['GET'])
def shopcategory_detail(_id, slug):
    form = ShopCategoryForm()
    shopcategory_obj = ShopCategory.query.filter_by(id=_id, slug=slug).first()
    product_objs = Product.query.filter_by(shopcategory_id=shopcategory_obj.id).all()
    shop_user_id = shopcategory_obj.user_id
    shop_user_obj = User.query.get_or_404(shop_user_id)
    shopcategory_profile = db.session.query(Profile).filter_by(user_id=shop_user_id).first()
    cover_img_obj = db.session.query(ShopCategoryCoverImage).filter_by(shopcategory_id=shopcategory_obj.id).first()
    if shop_user_obj != current_user:
        shopcategory_obj.view_count += 1
        db.session.commit()
    return render_template('ecomm/products/shopcategory_detail.html',
                           shopcategory=shopcategory_obj,
                           product_objs=product_objs,
                           form=form,
                           cover_img=cover_img_obj,
                           target_profile=shopcategory_profile)


@products_bp.route('/shop-category/existing/check/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def existing_shopcategory_check_ajax(_id):
    """상점카테고리 타이틀을 체크하는 ajax"""
    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).first()
    title = request.form.get("title")
    print(title)
    if title:
        existing_title = ShopCategory.query.filter_by(title=title).first()
        if existing_title and (title != shopcategory.title):
            # flash("동일한 닉네임이 존재합니다.")
            shop_data_response = {
                "flash_message": "동일한 상점타이틀이 존재합니다.",
            }
        elif existing_title and (title == shopcategory.title):
            shop_data_response = {
                "flash_message": "상점타이틀이 그전과 동일해요. (사용가능)",
            }
        else:
            # flash("사용가능한 닉네임입니다.")
            print("else========================")
            shop_data_response = {
                "flash_message": "사용가능한 상점타이틀입니다.",
            }
        return make_response(jsonify(shop_data_response))


data_response = ""


@products_bp.route('/shop-category/update/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def shopcategory_update_ajax(_id):
    global data_response
    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).one()
    if request.method == 'POST':
        if shopcategory:
            title = request.form.get("title")
            content = request.form.get("content")
            meta_description = request.form.get("meta_description")
            existing_title = ShopCategory.query.filter_by(title=title).first()
            if existing_title:
                if title != shopcategory.title:
                    print("다른 유저의 동일한 상점타이틀이 존재")
                    data_response = {
                        "flash_message": "동일한 상점타이틀이 존재합니다.",
                    }
                    return make_response(jsonify(data_response))
            if title and content and meta_description:
                shopcategory.title = title
                shopcategory.content = content
                shopcategory.meta_description = meta_description
                db.session.add(shopcategory)
                db.session.commit()

                data_response = {
                    "shopcategory_title": shopcategory.title,
                    "shopcategory_content": shopcategory.content,
                    "meta_description": shopcategory.meta_description,
                }
                return make_response(jsonify(data_response))
            elif not title:
                data_response = {
                    "checked_message": "상점타이틀를 채워주세요!",
                }
            elif not content:
                data_response = {
                    "checked_message": "간단 소개글를 채워주세요!",
                }
            elif not meta_description:
                data_response = {
                    "checked_message": "메타 설명를 채워주세요!",
                }
            return make_response(jsonify(data_response))
        else:
            abort(401)


@products_bp.route('/shop-category/list', methods=['GET'])
def shopcategory_list():
    shopcategories = ShopCategory.query.order_by(desc(ShopCategory.created_at))
    return render_template('ecomm/products/shopcategory_list.html', shopcategories=shopcategories)


@products_bp.route('/shop-category/delete/ajax/<int:_id>', methods=['POST'])
@shopcategory_ownership_required
def shopcategory_delete_ajax(_id):
    """symbol_path and cover_image_path 둘다 삭제해야 한다."""
    shopcategory = db.session.query(ShopCategory).filter_by(id=_id).one()
    profile = db.session.query(Profile).filter_by(user_id=shopcategory.user_id).one()
    if request.method == 'POST':
        if shopcategory:
            try:
                symbol_image_origin_path = os.path.join(BASE_DIR, shopcategory.symbol_path)
                if os.path.isfile(symbol_image_origin_path):
                    shutil.rmtree(os.path.dirname(symbol_image_origin_path))
                existing_cover_img = db.session.query(ShopCategoryCoverImage).filter_by(shopcategory_id=shopcategory.id).first()
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
            db.session.delete(shopcategory)
            db.session.commit()
            shop_data_response = {
                "profile_vendor_detail_url": url_for('profiles.vendor_detail', _id=profile.id)
            }
            return make_response(jsonify(shop_data_response))
        abort(401)


@products_bp.route('/shop-category/subscribe/ajax/<int:_id>', methods=['POST'])
@login_required
def shopcategory_subscribe_ajax(_id):
    global data_response
    if request.method == 'POST':
        _shopcategory = ShopCategory.query.get_or_404(_id)
        if g.user == _shopcategory.user:
            flash('본인이 작성한 글은 추천할수 없습니다')
        else:
            if current_user in _shopcategory.subscribers:
                print("OK:: 이미 구독중")
                data_response = {
                    "checked_message": "이미 구독하고 계세요!"
                }
            else:
                print("pre-subscribe::_shopcategory.subscribers", _shopcategory.subscribers)
                _shopcategory.subscribers.append(g.user)
                db.session.commit()
                subscribe_count = len(_shopcategory.subscribers)  # 제대로 되는지 확인
                print("post-subscribe::_shopcategory.subscribers", _shopcategory.subscribers)
                print(subscribe_count)
                data_response = {
                    "subscribe_count": subscribe_count
                }
            return make_response(jsonify(data_response))
    abort(401)


@products_bp.route('/shop-category/subscribe/cancel/ajax/<int:_id>', methods=['POST'])
@login_required
def shopcategory_subscribe_cancel_ajax(_id):
    global data_response
    if request.method == 'POST':
        _shopcategory = ShopCategory.query.get_or_404(_id)
        print("pre-cancel::_shopcategory.subscribers", _shopcategory.subscribers)
        if current_user in _shopcategory.subscribers:
            _shopcategory.subscribers.remove(g.user)
            db.session.commit()
            subscribe_count = len(_shopcategory.subscribers)
            print("post-cancel::_shopcategory.subscribers", _shopcategory.subscribers)
            print("subscribe_count", subscribe_count)
            data_response = {
                "flash_message": "그동안 구독해주셔서 감사해요!",
                "subscribe_count": subscribe_count
            }
        else:
            data_response = {
                "checked_count": "구독했던 유저만 취소가 가능해요!"
            }
        return make_response(jsonify(data_response))
    abort(401)


@products_bp.route('/product/create', methods=['GET', 'POST'])
@vendor_required
def product_create():
    form = ProductForm()
    if request.method == 'POST':  # and form.validate_on_submit():
        title = form.title.data
        content = request.form.get('content')
        shopcategory_id = int(request.form.get('shopcategory_id').split("?")[1].split("&")[0].split("=")[1])
        orm_id = request.form.get('orm_id')

        new_product = Product(
            user_id=g.user.id,
            title=title
        )
        new_product.shopcategory_id = shopcategory_id
        new_product.orm_id = orm_id
        new_product.subject = title

        new_product.content = content
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('products.product_detail', _id=new_product.id, slug=new_product.slug))
    else:
        products_all = Product.query.all()
        try:
            new_id = str(products_all[-1].id + 1)  # 고유해지지만, model.id와 일치하지는 않는다. 삭제된 놈들이 있으면...
        except Exception as e:
            print(e)
            new_id = str(1)
        user_id = str(g.user.id)
        random_string = str(uuid.uuid4())
        username = g.user.email.split('@')[0]
        orm_id = user_id + ":" + username + ":" + new_id + ":" + random_string
    return render_template('ecomm/products/product/create.html', form=form, orm_id=orm_id)


@products_bp.route('/product_units_images/save/ajax', methods=['POST'])
@vendor_required
def units_images_save_ajax():
    """sun_image_ajax이미지 저장하고,
    response로 contenteditable div의 figure > img src에 setAttribute를
    filePath로 replace시켜야 한다. 현재는 base64 data로 되어있다."""
    ajax_post_key()
    post_key = session["ajax_post_key"]
    if post_key and request.method == 'POST':
        image_string = request.form.get('upload_img')
        file_name = request.form.get('file_name')
        orm_id = request.form.get('orm_id')
        img_alt = request.form.get('alt')
        image_path, file_name = base64_to_file(image_string, file_name)
        """
        # 원판
        print('YYYYYYYYYYYYYYYYYY',request.files)
        # sun_image = form.data.get('upload_img')
        image_path = request.files.get("upload_img")

        # sun_image = request.files['upload_img'] # 위와 같다.
        print('nnnnnnnnnnnnnnnnnnnnnn filename', image_path)
        print('nnnnnnnnnnnnnnnnnnnnnn filename', image_path.filename)
        # print('nnnnnnnnnnnnnnnnnnnnnn filename', request.files.get("filename"))
        # filename = request.files.get("filename")
        """

        new_units_image = UnitsProductImage(
            user_id=g.user.id,
            orm_id=orm_id,
        )
        if image_path:
            new_units_image.image_path = image_path
            new_units_image.original_filename = file_name
            """
            # 원판
            relative_path, _ = save_file(NOW, image_path)
            new_image_path.image_path = relative_path
            new_image_path.original_filename = image_path.filename
            """

        """path로 저장하지 않으면, 즉...new_sun_image.sun_image = sun_image 로 저장하면,
         base64 data 형태인 file <FileStorage: '9952F23B5D2C1E3D1F.png' ('image/png')>로 저장된다."""
        db.session.add(new_units_image)
        db.session.commit()
        session.pop('ajax_post_key', None)
        units_data_response = {
            "image_path": new_units_image.image_path,
            "orm_id": orm_id,
            "origin_filename": file_name
        }
        return make_response(jsonify(units_data_response))
    else:
        return make_response(jsonify({"image_path": 'else error'}))


@products_bp.route('/product/detail/<int:_id>/<slug>', methods=['GET'])
def product_detail(_id, slug):
    product_obj = Product.query.filter_by(id=_id, slug=slug).first()
    return render_template('ecomm/products/product/detail.html', product_obj=product_obj)


@products_bp.route('/product/update/<int:_id>/<slug>', methods=['GET', 'POST'])
@product_ownership_required
def product_update(_id, slug):
    product_obj = Product.query.filter_by(id=_id, slug=slug).first()
    shopcategory_objs = ShopCategory.query.all()
    shopcategory_obj = ShopCategory.query.filter_by(id=product_obj.shopcategory_id).first()
    orm_id = product_obj.orm_id
    if g.user != product_obj.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('products.product_detail', _id=_id, slug=slug))
    if request.method == 'POST':  # POST 요청
        form = ProductForm()
        if not request.form.get('content'):
            flash('변경 내용을 적어주세요!')
            return redirect(url_for('products.product_detail', _id=_id, slug=slug))

        title = form.title.data
        content = request.form.get('content')

        product_obj.title = title
        product_obj.content = content
        db.session.add(product_obj)
        db.session.commit()
        """ # 저장후에 content 의 src 를, DB와 비교해서, DB 에 있으나 content 에는 없는 image(file, path)를 삭제"""
        try:
            db_img_objs_all = product_obj.product_unitsproductimage_set
            content_html = product_obj.content
            import lxml.html
            html = lxml.html.fromstring(content_html)
            img_tags = html.xpath("//img")
            content_img_objs_all = []
            for img_tag in img_tags:
                file_path = "static" + img_tag.attrib["src"].split("static")[1]
                content_img_obj = UnitsProductImage.query.filter_by(image_path=file_path).first()
                content_img_objs_all.append(content_img_obj)
            unused_db_img_objs = set(db_img_objs_all) - set(content_img_objs_all)
            """DB_image 와 content_image 들을 비교해서 필요없는 DB_image 모두 삭제하기"""
            print("삭제전 모든 이미지::: product.product_unitsproductimage_set========", product_obj.product_unitsproductimage_set)
            print("content_img_objs_all ====================================", content_img_objs_all)
            print("unused_db_img_objs=======================================", unused_db_img_objs)
            if unused_db_img_objs:
                for unused_db_img_obj in unused_db_img_objs:
                    try:
                        unused_db_img_path = os.path.join(BASE_DIR, unused_db_img_obj.image_path)
                        if os.path.isfile(unused_db_img_path):
                            shutil.rmtree(os.path.dirname(unused_db_img_path))
                    except Exception as e:
                        print(e)
                    db.session.delete(unused_db_img_obj)
                    db.session.commit()
        except Exception as e:
            print('product_update exception error::', e)
        return redirect(url_for('products.product_detail', _id=_id, slug=slug))
    else:
        print('0000000000000000000000 else  # GET 요청', product_obj)
        form = ProductForm()
    return render_template('ecomm/products/product/update.html', form=form,
                           product_obj=product_obj, shopcategory_obj=shopcategory_obj,
                           shopcategory_objs=shopcategory_objs, orm_id=orm_id)


@products_bp.route('/product/vote/ajax/<int:_id>', methods=['POST'])
@login_required
def product_vote_ajax(_id):
    pass
