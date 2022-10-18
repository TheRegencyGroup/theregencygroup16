from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        unconfirmed_agreements = self.mapped('order_line').filtered(lambda s: s.consumption_agreement_line_id
                                                                  and s.consumption_agreement_line_id.state == 'draft')
        if unconfirmed_agreements:
            agreements = ','.join(unconfirmed_agreements.mapped('consumption_agreement_line_id.agreement_id.name'))
            raise UserError('You can not confirm sale orders with assigned draft consumption agreement %s. '
                            'Please, confirm agreement first.' % agreements)
        res = super(SaleOrder, self).action_confirm()
        self.mapped('order_line').check_overconsumption()
        self.mapped('order_line').check_fifo_consumption()
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    consumption_agreement_line_id = fields.Many2one('consumption.agreement.line')
    qty_remaining = fields.Integer(related='consumption_agreement_line_id.qty_remaining')
    partner_id = fields.Many2one(related='order_id.partner_id')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.link_overlay_to_product()
        return res

    def link_overlay_to_product(self):
        for line in self:
            attribute_ids = line.product_template_attribute_value_ids.mapped('attribute_id')
            if self.env.ref('regency_shopsite.overlay_attribute') in attribute_ids and self.env.ref(
                    'regency_shopsite.customization_attribute') in attribute_ids:
                for overlay_product in line.product_template_id.overlay_template_ids.mapped('overlay_product_ids'):
                    overlay_product.product_id = line.product_id.id

    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        self.consumption_agreement_line_id = self.env['consumption.agreement.line'].\
            search([('product_id', '=', self.product_id.id),
                    ('qty_remaining', '>', 0),
                    '|', ('allowed_partner_ids', 'in', self.partner_id.id),
                         '&', ('allowed_partner_ids', '=', False),
                              ('agreement_id.allowed_partner_ids', 'in', self.partner_id.id)],
                   order='signed_date',
                   limit=1)
        self.price_unit = self.consumption_agreement_line_id.price_unit

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super(SaleOrderLine, self).product_uom_change()
        if self.consumption_agreement_line_id:
            self.price_unit = self.consumption_agreement_line_id.price_unit

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'product_uom_qty' in vals:
            self.check_overconsumption()
        if 'state' in vals and 'product_uom_qty' in vals or 'consumption_agreement_line_id' in vals:
            self.check_fifo_consumption()
        return res

    def check_overconsumption(self):
        for rec in self.mapped('consumption_agreement_line_id'):
            rec._compute_qty_consumed()
            if rec.qty_consumed > rec.qty_allowed:
                raise UserError('Accordingly to agreement %s you can not consume more than %s of %s' % (
                    rec.agreement_id.name, rec.qty_allowed, rec.product_id.name))

    def check_fifo_consumption(self):
        for rec in self.filtered(lambda s: s.consumption_agreement_line_id
                                    and s.consumption_agreement_line_id.state == 'confirmed'
                                    and s.order_id.state == 'sale'):
            rec.consumption_agreement_line_id._compute_qty_consumed()
            # there are no open agreements with same product before assigned agreement
            previous_lines = self.env['consumption.agreement.line'].search([('signed_date', '<', rec.consumption_agreement_line_id.signed_date),
                                                           ('product_id', '=', rec.product_id.id),
                                                           ('qty_remaining', '>', 0),
                                                           ('state', '=', 'confirmed'),
                                                           '|', ('allowed_partner_ids', 'in', rec.partner_id.id),
                                                               '&', ('allowed_partner_ids', '=', False),
                                                               (
                                                               'agreement_id.allowed_partner_ids', 'in', rec.partner_id.id)
                                                           ], limit=1)
            if previous_lines:
                raise UserError('You can not consume from agreement %s, because there are earlier agreement  %s  with available quantity of %s' % (
                    rec.consumption_agreement_line_id.agreement_id.name, previous_lines.agreement_id.name, rec.product_id.name))

