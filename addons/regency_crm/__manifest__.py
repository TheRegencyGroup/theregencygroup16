{
    'name': 'Regency CRM',
    'version': '16.0.0.7.0',
    'summary': '',
    'author': 'OpsWay',
    'description': "",
    'depends': [
        'sale_crm',
        'utm',
        'regency_estimate',
    ],
    'category': 'Regency/CRM',
    'sequence': 10,
    'data': [
        'views/crm_lead.xml',
        'views/crm_stage.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}
