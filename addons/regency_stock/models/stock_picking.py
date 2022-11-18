from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_print_packges(self):
        return self.env.ref('stock.action_report_quant_package_barcode_small').report_action(self.package_ids)
