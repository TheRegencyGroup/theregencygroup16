from odoo import fields, models, api


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    partner_id = fields.Many2one(domain=[('is_company', '=', True), ('is_vendor', '=', True)])
