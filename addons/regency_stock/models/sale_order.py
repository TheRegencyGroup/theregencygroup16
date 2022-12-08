from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def set_delivery_line(self, carrier, amount):
        """
        Set carrier on pickings.
        """
        res = super(SaleOrder, self).set_delivery_line(carrier, amount)
        for order in self:
            out_stock_picking = order.mapped('order_line.move_ids.picking_id').filtered(
                lambda f: f.picking_type_code == 'outgoing')
            if out_stock_picking:
                out_stock_picking.write({'carrier_id': carrier.id})
        return res
