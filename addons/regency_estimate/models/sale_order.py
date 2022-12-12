from odoo import fields, models
from odoo.addons.regency_tools.system_messages import accept_format_string, SystemMessages


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    price_sheet_id = fields.Many2one('product.price.sheet')
    estimate_id = fields.Many2one('sale.estimate')
    legal_accepted = fields.Boolean(default=False)

    def _has_to_be_signed(self, include_draft=False):
        return super(SaleOrder, self)._has_to_be_signed(include_draft=True)

    def toggle_legal_accepted(self, checked):
        self.ensure_one()
        if self.state == 'draft':
            self.legal_accepted = checked
        return self.legal_accepted

    def action_confirm(self):
        res = super().action_confirm()
        if self.estimate_id:
            partners_to_inform = self.env['res.partner']
            if self.estimate_id.estimate_manager_id:
                partners_to_inform += self.estimate_id.estimate_manager_id.partner_id
            if self.estimate_id.purchase_agreement_ids:
                for partner in self.estimate_id.purchase_agreement_ids.mapped('user_id.partner_id'):
                    partners_to_inform += partner
            for partner in partners_to_inform:
                msg = accept_format_string(SystemMessages.get('M-011'), partner.name, self.name)
                self.message_post(body=msg, partner_ids=partner.ids)
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricesheet_line_id = fields.Many2one('product.price.sheet.line')

    def _compute_tax_id(self):
        """
            Temporary disable taxes calculation
        :return:
        """
        #TODO: uncomment when taxes will be handled in a correct way
        pass

    def get_purchase_order_lines(self):
        return self.purchase_line_ids |\
               self.order_id.procurement_group_id.stock_move_ids.filtered(lambda x: x.product_id == self.product_id).created_purchase_line_id |\
               self.order_id.procurement_group_id.stock_move_ids.filtered(lambda x: x.product_id == self.product_id).move_orig_ids.purchase_line_id
