{
    'name': 'Regency Sales Estimates',
    'version': '16.0.0.12',
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
        'regency_backend_interface',
        'mail_chatter_customization',
        'product',
        'regency_tools',
        'multi_currency_widget'
    ],
    'category': 'Regency/Sales',
    'sequence': 10,
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'report/report_inherit_purchase_order.xml',
        'data/product_price_sheet.xml',
        'data/purchase_requisition_data.xml',
        'data/sale_estimate_sequence.xml',
        'wizard/cancellation_purchase_order.xml',
        'views/sale_estimate.xml',
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
        'views/portal_templates.xml',
        'views/fee_type.xml',
        'views/fee_value.xml',
        'data/fee_type.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/res_config_settings.xml',
        'data/ir_rules.xml',
    ],
    'demo': [
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
