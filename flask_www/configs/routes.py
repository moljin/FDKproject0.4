def routes_init(app):
    from flask_www.commons import common
    app.register_blueprint(common.common_bp)

    from flask_www.accounts import accounts, profiles
    app.register_blueprint(accounts.accounts_bp)
    app.register_blueprint(profiles.profiles_bp)

    from flask_www.ecomm.products import products
    app.register_blueprint(products.products_bp)



