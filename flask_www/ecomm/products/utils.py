from flask_www.commons.utils import new_three_image_save
from flask_www.configs import db
from flask_www.ecomm.products.models import ShopCategoryCoverImage


def new_shop_cover_image_save(user, shopcategory, image1, image2, image3, path):
    new_cover_image = ShopCategoryCoverImage()
    new_cover_image.user_id = user.id
    new_cover_image.shopcategory_id = shopcategory.id
    new_three_image_save(user, new_cover_image, image1, image2, image3, path)
    db.session.add(new_cover_image)
