from odoo import api, fields, models, Command
from odoo.exceptions import UserError
import time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    consumption_agreement_id = fields.Many2one('consumption.agreement')

    # currency_id overridden according to the requirements in https://lumirang.atlassian.net/browse/REG-482
    # paragraph 8
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)

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
        self.add_downpayments_from_ca()
        return res

    def add_downpayments_from_ca(self):
        for rec in self:
            consumptions = rec.order_line.mapped('consumption_agreement_line_id.agreement_id')
            for con in consumptions.filtered(lambda x: x.deposit_percent > 0):
                lines = rec.order_line.filtered(lambda x: x.consumption_agreement_line_id.agreement_id.id == con.id)
                lines_subtotal = sum(lines.mapped('price_subtotal'))
                so_context = {
                    'active_model': 'sale.order',
                    'active_ids': [rec.id],
                    'active_id': rec.id
                }
                downpayment = self.env['sale.advance.payment.inv'].with_context(so_context).create({
                    'advance_payment_method': 'percentage',
                    'amount': con.deposit_percent
                })
                # Create down payment section if necessary
                if not any(line.display_type and line.is_downpayment for line in rec.order_line):
                    self.env['sale.order.line'].create(
                        downpayment._prepare_down_payment_section_values(rec)
                    )
                line_values = downpayment._prepare_so_line_values(rec)
                line_values['price_unit'] = downpayment._get_down_payment_amount_from_total(lines_subtotal) / len(con.invoice_ids)
                line_values['name'] = f"Down Payment: { con.name } Deposist { con.deposit_percent_str }"
                line_values['invoice_lines'] = [Command.link(invl.id) for invl in con.invoice_ids.mapped('line_ids').
                                                        filtered(lambda x: x.display_type == 'product')]
                self.env['sale.order.line'].create(line_values)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.country_id:
            self.currency_id = self.partner_id.country_id.currency_id.id

    @api.model
    def create(self, values):
        res = super().create(values)
        # onchange_partner_id not save currency changes
        customer_id = self.env['res.partner'].browse(values.get('partner_id'))
        if customer_id.country_id:
            values.update({'currency_id': customer_id.country_id.currency_id.id})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    consumption_agreement_line_id = fields.Many2one('consumption.agreement.line')
    qty_remaining = fields.Integer(related='consumption_agreement_line_id.qty_remaining')
    partner_id = fields.Many2one(related='order_id.partner_id')

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        super(SaleOrderLine, self)._onchange_product_id_warning()
        self.consumption_agreement_line_id = self.find_consumption_agreement(self.product_id, self.partner_id)
        if self.consumption_agreement_line_id:
            self.price_unit = self.consumption_agreement_line_id.price_unit

    @api.onchange('product_uom', 'product_uom_qty')
    def _compute_product_uom(self):
        super(SaleOrderLine, self)._compute_product_uom()
        if self.consumption_agreement_line_id:
            self.price_unit = self.consumption_agreement_line_id.price_unit

    def find_consumption_agreement(self, product_id, partner_id):
        return self.env['consumption.agreement.line'].\
            search([('product_id', '=', product_id.id),
                    ('qty_remaining', '>', 0),
                    '|', ('allowed_partner_ids', 'in', partner_id.id),
                         '&', ('allowed_partner_ids', '=', False),
                              ('agreement_id.allowed_partner_ids', 'in', partner_id.id)],
                   order='signed_date',
                   limit=1)

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

