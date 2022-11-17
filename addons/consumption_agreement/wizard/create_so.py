from odoo import fields, models, _
from odoo.addons.regency_tools import SystemMessages


class SaleOrderCAWizard(models.TransientModel):
    _name = 'sale.order.ca.wizard'
    _description = 'CA Sale Order'

    consumption_agreement_id = fields.Many2one('consumption.agreement')
    ca_line_ids = fields.One2many('sale.order.ca.line.wizard', 'sale_order_ca_id')

    def create_so_from_ca(self):
        order, order_count = self.consumption_agreement_id.create_sale_order(
            selected_line_ids=self.ca_line_ids.filtered(lambda f: f.selected).mapped('consumption_agreement_line_id').ids)
        if not order_count:
            action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = order.id
            return action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(SystemMessages.get('M-010') % order.name),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }


class SaleOrderCALineWizard(models.TransientModel):
    _name = 'sale.order.ca.line.wizard'
    _description = 'CA Sale Order line'

    sale_order_ca_id = fields.Many2one('sale.order.ca.wizard')
    consumption_agreement_line_id = fields.Many2one('consumption.agreement.line')
    selected_qty = fields.Integer(related='consumption_agreement_line_id.qty_allowed')
    product_id = fields.Many2one('product.product', related='consumption_agreement_line_id.product_id')
    selected = fields.Boolean(default=True)
