from odoo import fields, models


class CustomerAssociation(models.Model):
    _name = 'customer.association'

    CUSTOMER_ASSOCIATION_TYPE = [
        ('ownership', 'Ownership'),
        ('asset_management', 'Asset Management'),
        ('hotel_management', 'Hotel Management'),
        ('brand_management', 'Brand Management'),
        ('producer', 'Producer')
    ]

    external_child_code = fields.Char()
    related_partner_id = fields.Many2one('res.partner')
    parent_partner_id = fields.Many2one('res.partner', string='Parent')
    type = fields.Selection(CUSTOMER_ASSOCIATION_TYPE, required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date()
