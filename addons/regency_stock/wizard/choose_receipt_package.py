from odoo import fields, models


class ChooseReceiptPackage(models.TransientModel):
    _name = 'choose.receipt.package'
    _description = 'Receipt Package Selection Wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    receipt_package_type_id = fields.Many2one('stock.package.type', 'Receipt Package Type', check_company=True)
    receipt_weight = fields.Float('Shipping Weight')

    def action_put_in_pack(self):
        pass
