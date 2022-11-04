{
    'name': 'Regency Sales Estimates',
    'version': '16.0.0.4',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'depends': [
        'sale_crm',
        'product_copy_template',
        'sale_product_configurator',
        'purchase_requisition',
        'consumption_agreement',
        'dr_many_tags_link',
        'sale_management',
        'web_one2many_duplicate_cr',
        'delivery',
        'stock_mts_mto_rule',
        'custom_list_view',
    ],
    'category': 'Regency/Sales',
    'sequence': 10,
    'data': [
        'data/product_price_sheet.xml',
        'data/sale_estimate_stages.xml',
        'data/purchase_requisition_data.xml',
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/sale_estimate.xml',
        'views/sale_estimate_stage_views.xml',
        'views/purchase_requisition_views.xml',
        'views/product_price_sheet.xml',
        'views/purchase_views.xml',
        'views/sale_portal_templates.xml',
        'views/purchase_views.xml',
        'wizard/previous_prices_view.xml',
        'views/res_partner.xml',
        'views/price_sheet_portal.xml',
        'views/crm_lead.xml',
        'views/crm_stage.xml',
        'wizard/choose_delivery_carrier_view.xml',
        'wizard/portal_link.xml',
        'views/product_views.xml',
        'views/delivery_carrier.xml',
        'views/portal_templates.xml'
    ],
    'demo': [
        'data/product_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'regency_estimate/static/src/frontend/js/**/*.js',
            'regency_estimate/static/src/scss/frontend/*.scss',
        ],
        'web.assets_backend': [
            'regency_estimate/static/src/js/**/*',
            'regency_estimate/static/src/scss/backend/*.scss',
            'regency_estimate/static/src/xml/qty_at_date_widget.xml'
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
