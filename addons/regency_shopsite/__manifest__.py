{
    'name': 'Regency Shopsite',
    'version': '16.0.0.2',
    'author': 'OpsWay',
    'depends': [
        'website_sale',
        'fe_owl_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/overlay_position.xml',
        'data/product_attribute.xml',
        'data/ir_config_parameter.xml',
        'views/sale_order_view.xml',
        'views/web_layout.xml',
        'views/website_cart_lines.xml',
        'views/website_variant_templates.xml',
        'views/website_overlay_template_page.xml',
        'views/overlay_template_view.xml',
        'views/overlay_position_view.xml',
        # 'views/product_pricelist_item_view.xml',
        'views/product_product.xml',
        'views/sale_portal_templates.xml',
        'views/shopsite_catalog.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'regency_shopsite/static/lib/*.js',
            'regency_shopsite/static/src/js/main.js',
            'regency_shopsite/static/src/js/frontend/overlay_template_page/*.js',
            'regency_shopsite/static/src/scss/frontend/*.scss',
            'regency_shopsite/static/src/xml/templates_frontend.xml',
        ],
        'web.assets_backend': [
            'regency_shopsite/static/lib/*.js',
            'regency_shopsite/static/src/js/main.js',
            'regency_shopsite/static/src/js/backend/*.js',
            'regency_shopsite/static/src/scss/backend/*.scss',
            'regency_shopsite/static/src/xml/templates_backend.xml',
        ],
    },
    'category': 'Regency',
    'installable': True,
    'application': True,
    'auto_install': False,
}
