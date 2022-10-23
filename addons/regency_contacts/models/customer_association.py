from odoo import fields, models


class CustomerAssociation(models.Model):
    _name = 'customer.association'
    _description = 'Customer association'


    association_type = fields.Many2one('association.type')
    left_partner_id = fields.Many2one('res.partner')
    right_partner_id = fields.Many2one('res.partner', domain=[('contact_type', '=', 'customer')])


class AssociationType(models.Model):
    _name = 'association.type'
    _description = 'Association type'

    name = fields.Char()
    left_to_right_name = fields.Char()
    right_to_left_name = fields.Char()
