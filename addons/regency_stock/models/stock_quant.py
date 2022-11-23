from odoo import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _compute_customer_ids(self):
        customer_ids = False
        if self.package_id:
            domain = ['|', ('result_package_id', '=', self.package_id.id), ('package_id', '=', self.package_id.id)]
            incoming_picking_ids = self.env['stock.move.line'].search(domain).mapped('picking_id').filtered(
                lambda f: f.picking_type_id.code == 'incoming')
            for req in incoming_picking_ids:
                pol = req.move_ids.purchase_line_id
                customer_ids = pol.customer_id or req.product_id.product_tmpl_id.allowed_partner_ids or False
        return customer_ids
