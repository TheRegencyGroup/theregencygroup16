from odoo import models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_print_barcode_pdf(self):
        quants = self.package_ids.mapped('quant_ids')
        return self.env['stock.quant.package'].print_barcode(quants=quants)

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
        context = dict(self.env.context, default_picking_id=self.id)
        if self.product_id.packaging_ids and len(self.product_id.packaging_ids) == 1:
            context.update({
                'default_receipt_package_type_id': self.product_id.packaging_ids.package_type_id.id,
                'default_weight': self.product_id.packaging_ids.product_id.weight
            })
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
