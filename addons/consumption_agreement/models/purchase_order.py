from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    consumption_agreement_id = fields.Many2one('consumption.agreement')
