{
    'name': 'Regency Shopsite',
    'version': '16.0.0.10',
    'author': 'OpsWay',
    'license': "Other proprietary",
    'depends': [
        'sale',
        'website',
        'website_sale',
        'fe_owl_base',
        'product',
        'regency_contacts',
        'eq_sale_multi_delivery_address',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'security/groups.xml',
        'data/overlay_position.xml',
        'data/product_attribute.xml',
        'data/ir_config_parameter.xml',
        'views/sale_order_view.xml',
        'views/website/web_frontend_layout.xml',
        'views/website/website_header.xml',
        'views/website/website_footer.xml',
        'views/website/website_cart_lines.xml',
        'views/website/website_variant_templates.xml',
        'views/website/website_overlay_template_page.xml',
        'views/website/website_shop_catalog_page.xml',
        'views/overlay_template_view.xml',
        'views/overlay_position_view.xml',
        'views/overlay_product.xml',
        'views/product_pricelist_item_view.xml',
        'views/product_product.xml',
        'views/website/sale_portal_templates.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'views/sale_portal_templates.xml',
        'views/product_image_views.xml'
    ],
    'demo': [
        'data/demo/product_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'regency_shopsite/static/lib/**/*.js',
            'regency_shopsite/static/src/js/main.js',
            'regency_shopsite/static/src/js/frontend/header/*.js',
            'regency_shopsite/static/src/js/frontend/overlay_template_page/**/*.js',
            'regency_shopsite/static/src/js/frontend/cart/**/*.js',
            'regency_shopsite/static/src/js/frontend/shop_catalog/*.js',
            'regency_shopsite/static/src/js/frontend/list_pagination/*.js',

            'regency_shopsite/static/src/js/frontend/**/**/*.xml',

            'regency_shopsite/static/lib/**/*.css',
            'regency_shopsite/static/lib/**/*.scss',
            'regency_shopsite/static/src/scss/frontend/variables.scss',
            'regency_shopsite/static/src/scss/frontend/fonts/*.scss',
            'regency_shopsite/static/src/scss/frontend/base/mixins.scss',
            'regency_shopsite/static/src/scss/frontend/base/*.scss',
            'regency_shopsite/static/src/scss/frontend/layout/*.scss',
            'regency_shopsite/static/src/scss/frontend/partials/*.scss',
            # 'regency_shopsite/static/src/scss/frontend/vendors/*.scss',
            'regency_shopsite/static/src/scss/frontend/designer.scss',
        ],
        'web.assets_backend': [
            'regency_shopsite/static/lib/*.js',
            'regency_shopsite/static/src/js/main.js',
            'regency_shopsite/static/src/js/backend/*.js',

            'regency_shopsite/static/src/js/backend/*.xml',

            'regency_shopsite/static/src/scss/backend/*.scss',
        ],
    },
    'category': 'Regency',
    'sequence': 5,
    'installable': True,
    'application': True,
    'auto_install': False,
}
