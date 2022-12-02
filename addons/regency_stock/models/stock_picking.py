from odoo import models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_print_barcode_pdf(self):
        quants = self.package_ids.mapped('quant_ids')
        if quants:
            return self.env.ref('regency_stock.action_report_quant_package_barcode_small_quants').report_action(quants)
        return self.env.ref('regency_stock.action_report_quant_package_barcode_small_packages').report_action(self.package_ids)

    def _pre_put_in_pack_hook(self, move_line_ids):
        """
        Override: pu in pack Receipts.
        """
        res = super()._pre_put_in_pack_hook(move_line_ids)
        if not res and self.picking_type_code == 'incoming':
            return self._set_receipt_package_type()
        else:
            return res

    def _set_receipt_package_type(self):
        self.ensure_one()
        view_id = self.env.ref('regency_stock.choose_receipt_package_view_form').id
        context = dict(
            self.env.context,
            default_receipt_package_type_id=self.product_id.packaging_ids[0].package_type_id.id if len(
                self.product_id.packaging_ids) > 1 else self.product_id.packaging_ids.package_type_id.id
        )
        return {
            'name': _('Package Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.receipt.package',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }
