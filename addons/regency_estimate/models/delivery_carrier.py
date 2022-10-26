from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('other', 'Other')], ondelete={
        'other': lambda records: records.write({'delivery_type': 'fixed', 'fixed_price': 0})})
