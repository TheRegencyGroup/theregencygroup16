from odoo import fields, models


class SaleEstimate(models.Model):
    _inherit = 'sale.estimate'

    stock_picking_ids = fields.One2many(compute='_compute_stock_picking_ids')
    pickings_count = fields.Integer(compute='_compute_pickings_count')
    stock_picking_batch_ids = fields.One2many(compute='_compute_stock_picking_batch_ids')
    batch_pickings_count = fields.Integer(compute='_compute_batch_pickings_count')


    def _compute_stock_picking_ids(self):
        for se in self:
            se.stock_picking_ids = se.mapped('sale_order_ids.picking_ids').ids
            se.stock_picking_batch_ids = se.mapped('sale_order_ids.picking_ids.batch_id').ids

    def _compute_stock_picking_batch_ids(self):
        for se in self:
            se.stock_picking_batch_ids = se.mapped('sale_order_ids.picking_ids.batch_id').ids

    def _compute_pickings_count(self):
        for se in self:
            se.pickings_count = len(se.stock_picking_ids)

    def _compute_batch_pickings_count(self):
        for se in self:
            se.batch_pickings_count = len(se.mapped('sale_order_ids.picking_ids.batch_id'))

    def action_view_pickings(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('id', '=', self.stock_picking_ids.ids)]
        return action

    def action_view_batch_pickings(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock_picking_batch.stock_picking_batch_action")
        action['domain'] = [('id', '=', self.mapped('sale_order_ids.picking_ids.batch_id').ids)]
        return action
