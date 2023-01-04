from odoo import models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    def print_barcode(self, stock_move_line=False, quants=False):
        quants = quants or self.quant_ids
        if quants:
            return self.env.ref('regency_stock.action_report_quant_package_barcode_small_quants').report_action(quants)
        stock_move_line = stock_move_line or self.env['stock.move.line'].search([('result_package_id', '=', self.id)])
        if stock_move_line:
            report_action = self.env.ref(
                'regency_stock.action_report_quant_package_barcode_small_stock_move_line').report_action(stock_move_line)
            report_action.update({'close_on_report_download': True})
            return report_action
