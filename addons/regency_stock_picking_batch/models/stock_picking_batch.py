from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    tracking_number = fields.Char()
    account_move_id = fields.Many2one('account.move', domain=[('move_type', '=', 'in_invoice')], string='Vendor Bill')
    landed_cost_ids = fields.One2many('stock.landed.cost', compute='_compute_landed_cost_ids')
    landed_cost_count = fields.Integer(compute='_compute_landed_costs_count')
    vendor_bill_ids = fields.One2many('account.move', compute='_compute_vendor_bill_ids')
    vendor_bills_count = fields.Integer(compute='_compute_vendor_bill_count')

    def _compute_vendor_bill_ids(self):
        for rec in self:
            rec.vendor_bill_ids = self.env['account.move'].browse(
                set([x.vendor_bill_id.id for x in rec.landed_cost_ids]))

    def _compute_vendor_bill_count(self):
        for rec in self:
            rec.vendor_bills_count = len(rec.vendor_bill_ids)

    def _compute_landed_cost_ids(self):
        for rec in self:
            rec.landed_cost_ids = self.env['stock.landed.cost'].search([('picking_batch_ids', 'in', self.id)])

    def _compute_landed_costs_count(self):
        for rec in self:
            rec.landed_cost_count = len(rec.landed_cost_ids)

    def open_landed_costs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        action['domain'] = [('id', 'in', self.landed_cost_ids.ids)]
        return action

    def open_vendor_bills(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        action['domain'] = [('id', 'in', self.vendor_bill_ids.ids)]
        return action
