from odoo import fields, models
from odoo.tools import float_compare


class ChooseReceiptPackage(models.TransientModel):
    _name = 'choose.receipt.package'
    _description = 'Receipt Package Selection Wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    receipt_package_type_id = fields.Many2one('stock.package.type', 'Receipt Package Type', check_company=True)
    weight = fields.Float('Shipping Weight')

    def action_put_in_pack(self):
        picking_move_lines = self.picking_id.move_line_ids
        if not self.picking_id.picking_type_id.show_reserved and not self.env.context.get('barcode_view'):
            picking_move_lines = self.picking_id.move_line_nosuggest_ids

        move_line_ids = picking_move_lines.filtered(lambda ml:
                                                    float_compare(ml.qty_done, 0.0,
                                                                  precision_rounding=ml.product_uom_id.rounding) > 0
                                                    and not ml.result_package_id
                                                    )
        if not move_line_ids:
            move_line_ids = picking_move_lines.filtered(lambda ml: float_compare(ml.reserved_uom_qty, 0.0,
                                                                                 precision_rounding=ml.product_uom_id.rounding) > 0 and float_compare(
                ml.qty_done, 0.0,
                precision_rounding=ml.product_uom_id.rounding) == 0)

        delivery_package = self.picking_id._put_in_pack(move_line_ids)
        if self.weight:
            delivery_package.shipping_weight = self.weight
        report_action = self.env.ref('stock.report_package_barcode_small').report_action(self.picking_id.package_ids)
        report_action.update({'close_on_report_download': True})
        return report_action
