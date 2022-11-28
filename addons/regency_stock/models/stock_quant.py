from odoo import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _picking_customer_id(self):
        """ Compute customer for picking. Called by report_package_barcode_small_regency_quants.
        :param: obj 'stock.quant'
        :return: obj 'res.partner'
        """
        self.ensure_one()
        customer_id = False
        if self.package_id:
            domain = ['|', ('result_package_id', '=', self.package_id.id), ('package_id', '=', self.package_id.id)]
            incoming_picking_ids = self.env['stock.move.line'].search(domain).mapped('picking_id').filtered(
                lambda f: f.picking_type_id.code == 'incoming')
            for picking in incoming_picking_ids:
                pol = picking.move_ids.purchase_line_id
                customer_id = pol.customer_id
                if customer_id:
                    break
                allowed_customer_ids = picking.product_id.product_tmpl_id.allowed_partner_ids
                if allowed_customer_ids:
                    customer_id = allowed_customer_ids[0]
                    break
        return customer_id
