{
    'name': 'Regency Sales Estimates',
    'version': '15.0.0.9',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'depends': [
        'crm',
        'product_copy_template',
        'sale_product_configurator',
        'purchase_requisition',
        'consumption_agreement',
        'dr_many_tags_link',
        'sale_management'
    ],
    'category': 'Regency/Sales',
    'sequence': 10,
    'data': [
        'data/product_price_sheet.xml',
        'data/sale_estimate_stages.xml',
        'security/ir.model.access.csv',
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
        'views/crm_stage.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'regency_estimate/static/src/js/**/*'
        ],
        'web.assets_backend': [
            'regency_estimate/static/src/scss/**/*'
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
