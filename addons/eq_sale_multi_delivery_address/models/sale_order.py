# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import api, models, fields, _


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    delivery_partner_id = fields.Many2one('res.partner', string="Delivery Address")

    @api.onchange('product_id')
    def onchange_product_partner(self):
        if not self.delivery_partner_id:
            self.delivery_partner_id = self.order_id.partner_shipping_id

    def _prepare_procurement_values(self, group_id=False):
        res = super(sale_order_line, self)._prepare_procurement_values(group_id)
        if self.delivery_partner_id:
            res.update({'partner_id': self.delivery_partner_id.id or self.order_id.partner_shipping_id.id or False})
        return res


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _key_assign_picking(self):
        keys = super(stock_move, self)._key_assign_picking()
        return keys + (self.partner_id,)

    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = super(stock_move, self)._search_picking_for_assignation()
        if self.sale_line_id and self.partner_id:
            picking = picking.filtered(lambda l: l.partner_id.id == self.partner_id.id)
            if picking:
                picking = picking[0]
        return picking

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: