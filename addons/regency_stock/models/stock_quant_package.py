from odoo import models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    def print_barcode(self):
        quants = self.quant_ids
        if quants:
            return self.env.ref('regency_stock.action_report_quant_package_barcode_small_quants').report_action(quants)
        return self.env.ref('regency_stock.action_report_quant_package_barcode_small_packages').report_action(self)
