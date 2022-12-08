import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import float_is_zero


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    advance_payment_method_for_ca = fields.Selection(
        selection=[
            ('percentage', "Down payment (percentage)"),
            ('fixed', "Down payment (fixed amount)"),
        ],
        string="Create Invoice",
        default='percentage',
        required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing,"
            "according to their invoicing policy (based on ordered or delivered quantity).")

    sale_order_ids = fields.Many2many(
        'sale.order', default=lambda self: not self.env.context.get('active_model') == 'consumption.agreement' and
                                           self.env.context.get('active_ids'))

    consumption_agreement_ids = fields.Many2many('consumption.agreement',
                                                 default=lambda self: self.env.context.get('active_model') == 'consumption.agreement' and
                                                                      self.env.context.get('active_ids'))

    #=== COMPUTE METHODS ===#

    @api.onchange('advance_payment_method_for_ca')
    def onchange_advance_payment_methods_for_ca(self):
        if self.consumption_agreement_ids:
            self.advance_payment_method = self.advance_payment_method_for_ca

    @api.depends('sale_order_ids', 'consumption_agreement_ids')
    def _compute_count(self):
        for wizard in self:
            wizard.count = len(wizard.sale_order_ids) + len(wizard.consumption_agreement_ids)

    # next computed fields are only used for down payments invoices and therefore should only
    # have a value when 1 unique SO is invoiced through the wizard
    @api.depends('sale_order_ids', 'consumption_agreement_ids')
    def _compute_currency_id(self):
        self.currency_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.currency_id = wizard.sale_order_ids and wizard.sale_order_ids.currency_id \
                    or wizard.consumption_agreement_ids and wizard.consumption_agreement_ids.currency_id

    @api.depends('sale_order_ids', 'consumption_agreement_ids')
    def _compute_company_id(self):
        self.company_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.company_id = wizard.sale_order_ids and wizard.sale_order_ids.company_id \
                    or wizard.consumption_agreement_ids and wizard.consumption_agreement_ids.company_id

    #=== ACTION METHODS ===#

    def create_invoices(self):
        if self.sale_order_ids:
            res = super(SaleAdvancePaymentInv, self).create_invoices()
            return res
        elif self.consumption_agreement_ids:
            self._create_invoices_for_consumptions()

            if self.env.context.get('open_invoices'):
                return self.consumption_agreement_ids.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    #=== BUSINESS METHODS ===#

    def _create_invoices_for_consumptions(self):
        self.consumption_agreement_ids.ensure_one()
        self = self.with_company(self.company_id)
        order = self.consumption_agreement_ids

        # Create deposit product if necessary
        if not self.product_id:
            self.product_id = self.env['product.product'].create(
                self._prepare_down_payment_product_values()
            )
            self.env['ir.config_parameter'].sudo().set_param(
                'sale.default_deposit_product_id', self.product_id.id)

        invoice = self.env['account.move'].sudo().create(
            self._prepare_invoice_values(order, self)
        ).with_user(self.env.uid)  # Unsudo the invoice after creation

        invoice.message_post_with_view(
            'mail.message_origin_link',
            values={'self': invoice, 'origin': order},
            subtype_id=self.env.ref('mail.mt_note').id)

        return invoice

    def _get_down_payment_amount_from_total(self, amount_total):
        self.ensure_one()
        if self.advance_payment_method == 'percentage':
            amount = amount_total * self.amount / 100
        else:  # Fixed amount
            amount = self.fixed_amount
        return amount

    def _prepare_invoice_line(self, **optional_values):
        """Prepare the values to create the new invoice line.

        :param optional_values: any parameter that should be added to the returned invoice line
        :rtype: dict
        """
        self.ensure_one()
        order = self.consumption_agreement_ids
        # analytic_distribution = {}
        amount_total = sum(order.line_ids.mapped("untaxed_amount"))
        res = {
            'display_type': 'product',
            'name': _('Down Payment: %s (Draft)', time.strftime('%m %Y')),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'discount': 0.0,
            'price_unit':  self._get_down_payment_amount_from_total(amount_total),
            #'analytic_distribution': analytic_distribution,
            'is_downpayment': True,
        }
        if optional_values:
            res.update(optional_values)
        return res
