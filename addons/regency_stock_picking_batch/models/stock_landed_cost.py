from odoo import api, fields, models


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    picking_batch_ids = fields.Many2many(
        'stock.picking.batch', string='Batch transfers',
        copy=False, states={'done': [('readonly', True)]})
    picking_ids = fields.Many2many(compute='_compute_picking_ids', store=True)

    @api.depends('picking_batch_ids')
    def _compute_picking_ids(self):
        for landed_cost in self:
            landed_cost.picking_ids = landed_cost.mapped('picking_batch_ids.picking_ids')
