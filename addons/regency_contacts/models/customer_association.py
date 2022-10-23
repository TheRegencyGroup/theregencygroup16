from odoo import fields, models


class CustomerAssociation(models.Model):
    _name = 'customer.association'

    # CUSTOMER_ASSOCIATION_TYPE = [
    #     ('ownership', 'Ownership'),
    #     ('asset_management', 'Asset Management'),
    #     ('hotel_management', 'Hotel Management'),
    #     ('brand_management', 'Brand Management'),
    #     ('producer', 'Producer')
    # ]
    #
    # type = fields.Selection(CUSTOMER_ASSOCIATION_TYPE)
    association_type = fields.Many2one('association.type')
    left_partner_id = fields.Many2one('res.partner')
    right_partner_id = fields.Many2one('res.partner')


class AssociationType(models.Model):
    _name = 'association.type'

    name = fields.Char()
    left_to_right_name = fields.Char()
    right_to_left_name = fields.Char()


# res_partner m2m to association customer association