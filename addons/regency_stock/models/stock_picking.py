from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_print_barcode_pdf(self):
        quants = self.package_ids.mapped('quant_ids')
        if quants:
            return self.env.ref('regency_stock.action_report_quant_package_barcode_small_quants').report_action(quants)
        return self.env.ref('regency_stock.action_report_quant_package_barcode_small_packages').report_action(self.package_ids)
