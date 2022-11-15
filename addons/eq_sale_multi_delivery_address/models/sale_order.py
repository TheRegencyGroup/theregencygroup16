# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import api, models, fields, Command


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_partner_id = fields.Many2one('res.partner', string="Hotel Name")
    possible_delivery_address_ids = fields.Many2many('res.partner', compute='_compute_possible_delivery_address_id')
    delivery_address_id = fields.Many2one('res.partner', string='Delivery Address',
                                          domain="[('id', 'in', possible_delivery_address_ids)]",
                                          default=lambda self: self._get_default_delivery_address_id())

    @api.onchange('delivery_partner_id')
    def _compute_possible_delivery_address_id(self):
        for sol in self:
            address_ids = sol.delivery_partner_id.child_ids.filtered(lambda partner: partner.type == 'delivery') \
                          or sol.delivery_partner_id
            sol.possible_delivery_address_ids = [Command.set(address_ids.ids)]

    @api.onchange('delivery_partner_id', 'possible_delivery_address_ids')
    def _compute_default_delivery_address_id(self):
        for sol in self:
            sol.delivery_address_id = sol._get_default_delivery_address_id()

    def _get_default_delivery_address_id(self):
        return self.possible_delivery_address_ids.ids[0] if self.possible_delivery_address_ids else False

    def write(self, values):
        res = super(SaleOrderLine, self).write(values)
        return res

    @api.onchange('product_id')
    def onchange_product_partner(self):
        if not self.delivery_partner_id:
            self.delivery_partner_id = self.order_id.partner_shipping_id

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id)
        if self.delivery_partner_id:
            res.update({'partner_id': self.delivery_partner_id.id or self.order_id.partner_shipping_id.id or False})
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _key_assign_picking(self):
        keys = super()._key_assign_picking()
        return keys + (self.partner_id,)

    def _search_picking_for_assignation(self):
        picking = super()._search_picking_for_assignation()
        if self.sale_line_id and self.partner_id:
            picking = picking.filtered(lambda l: l.partner_id.id == self.partner_id.id)
            if picking:
                picking = picking[0]
        return picking

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
