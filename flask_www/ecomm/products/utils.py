from flask_www.commons.utils import new_three_image_save, existing_img_and_dir_delete_without_update
from flask_www.configs import db
from flask_www.ecomm.products.models import ShopCategoryCoverImage


def new_shop_cover_image_save(user, shopcategory, image1, image2, image3, path):
    new_cover_image = ShopCategoryCoverImage()
    new_cover_image.user_id = user.id
    new_cover_image.shopcategory_id = shopcategory.id
    new_three_image_save(user, new_cover_image, image1, image2, image3, path)
    db.session.add(new_cover_image)


def try_shopcategory_delete_ajax(target_shop):
    if target_shop.symbol_path:
        existing_img_and_dir_delete_without_update(target_shop.symbol_path)
    existing_cover_img = db.session.query(ShopCategoryCoverImage).filter_by(shopcategory_id=target_shop.id).first()
    if existing_cover_img:
        if existing_cover_img.image_1_path:
            existing_img_and_dir_delete_without_update(existing_cover_img.image_1_path)
        if existing_cover_img.image_2_path:
            existing_img_and_dir_delete_without_update(existing_cover_img.image_2_path)
        if existing_cover_img.image_3_path:
            existing_img_and_dir_delete_without_update(existing_cover_img.image_3_path)
    db.session.delete(existing_cover_img)


def shop_disable_save(shop_objs):
    for shop in shop_objs:
        shop.available_display = False
        db.session.add(shop)


def product_disable_save(product_objs):
    for product in product_objs:
        product.available_display = False
        product.available_order = False
        db.session.add(product)
