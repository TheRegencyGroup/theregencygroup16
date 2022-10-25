from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    tracking_number = fields.Char()
    account_move_id = fields.Many2one('account.move', domain=[('move_type', '=', 'in_invoice')], string='Vendor Bill')
